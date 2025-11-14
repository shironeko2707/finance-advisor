import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz
import re
from functools import lru_cache
from collections import defaultdict

class OptimizedFinancialConfidenceCalculator:
    def __init__(self, retrieval_tables: List[pd.DataFrame]):
        """
        Initialize with a list of retrieval tables that serve as ground truth sources
        
        Args:
            retrieval_tables: List of DataFrames containing source financial data
        """
        self.retrieval_tables = retrieval_tables
        self.confidence_weights = {
            'exact_match': 0.5,
            'fuzzy_match': 0.1,
            'source_reliability': 0.3,
            'temporal_consistency': 0.1
        }
        
        # Pre-compute and cache expensive operations
        self._preprocess_tables()
    
    def _preprocess_tables(self):
        """Pre-process retrieval tables for faster lookup"""
        self.normalized_tables = []
        self.row_index_map = {}  # Maps normalized row names to original indices
        self.col_index_map = {}  # Maps normalized col names to original columns
        
        for table_idx, table in enumerate(self.retrieval_tables):
            # Normalize table values
            normalized_table = table.copy()
            
            # Create normalized index mapping for fast lookup
            for idx in table.index:
                norm_idx = self._normalize_text(str(idx))
                if norm_idx not in self.row_index_map:
                    self.row_index_map[norm_idx] = []
                self.row_index_map[norm_idx].append((table_idx, idx))
            
            # Create normalized column mapping
            for col in table.columns:
                norm_col = self._normalize_text(str(col))
                if norm_col not in self.col_index_map:
                    self.col_index_map[norm_col] = []
                self.col_index_map[norm_col].append((table_idx, col))
            
            # Pre-normalize all numeric values
            for idx in table.index:
                for col in table.columns:
                    try:
                        original_value = table.loc[idx, col]
                        normalized_value = self._normalize_financial_value(original_value)
                        normalized_table.loc[idx, col] = normalized_value
                    except Exception:
                        normalized_table.loc[idx, col] = np.nan
            
            self.normalized_tables.append(normalized_table)
    
    @lru_cache(maxsize=1000)
    def _normalize_text(self, text):
        """Cached text normalization"""
        return re.sub(r'[^\w\s]', '', text.lower().strip())
    
    def calculate_confidence_matrix(self, result_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate confidence scores for each cell in the result DataFrame (optimized)
        
        Args:
            result_df: The extracted DataFrame from LLM
            
        Returns:
            DataFrame with same structure containing confidence scores (0-1)
        """
        confidence_matrix = pd.DataFrame(
            index=result_df.index,
            columns=result_df.columns,
            dtype=float
        )
        
        # Pre-normalize result_df values
        normalized_result = result_df.copy()
        for row_idx, row in result_df.iterrows():
            for col_idx, cell_value in row.items():
                # Skip normalization for NaN or N/A values
                if (pd.isna(cell_value) or 
                    cell_value == '' or 
                    str(cell_value).upper() in ['N/A', 'NA', 'NULL', 'NONE']):
                    normalized_result.loc[row_idx, col_idx] = np.nan
                else:
                    normalized_result.loc[row_idx, col_idx] = self._normalize_financial_value(cell_value)
        
        # Vectorized confidence calculation
        for row_idx, row in result_df.iterrows():
            for col_idx, cell_value in row.items():
                # Skip confidence calculation for NaN, empty, or N/A cells
                if (pd.isna(cell_value) or 
                    cell_value == '' or 
                    str(cell_value).upper() in ['N/A', 'NA', 'NULL', 'NONE']):
                    confidence_matrix.loc[row_idx, col_idx] = np.nan
                else:
                    normalized_value = normalized_result.loc[row_idx, col_idx]
                    # Skip if normalization resulted in NaN
                    if pd.isna(normalized_value):
                        confidence_matrix.loc[row_idx, col_idx] = np.nan
                    else:
                        confidence_score = self._calculate_cell_confidence_optimized(
                            normalized_value, row_idx, col_idx, normalized_result
                        )
                        confidence_matrix.loc[row_idx, col_idx] = confidence_score
        
        return confidence_matrix
    
    def _calculate_cell_confidence_optimized(self, normalized_value, row_label, col_label, normalized_result_df):
        """Optimized confidence calculation for a single cell"""
        
        # 1. Fast exact and fuzzy match scores (combined for efficiency)
        exact_score, fuzzy_score = self._get_match_scores_combined(
            normalized_value, row_label, col_label
        )
        
        # 2. Source Reliability Score (simplified)
        source_score = self._get_source_reliability_score_fast(
            normalized_value, row_label, col_label
        )
        
        # 3. Temporal Consistency Score (vectorized)
        temporal_score = self._get_temporal_consistency_score_fast(
            normalized_value, row_label, col_label, normalized_result_df
        )
        
        # Weighted combination
        total_confidence = (
            exact_score * self.confidence_weights['exact_match'] +
            fuzzy_score * self.confidence_weights['fuzzy_match'] +
            source_score * self.confidence_weights['source_reliability'] +
            temporal_score * self.confidence_weights['temporal_consistency']
        )
        
        return min(1.0, max(0.0, total_confidence))
    
    def _get_match_scores_combined(self, normalized_value, row_label, col_label):
        """Combined exact and fuzzy matching for efficiency"""
        exact_matches = 0
        total_searches = 0
        best_fuzzy_score = 0
        
        # Ensure normalized_value is numeric
        if not isinstance(normalized_value, (int, float)) or np.isnan(float(normalized_value)):
            return 0.0, 0.0
        
        # Fast lookup using pre-computed mappings
        norm_row = self._normalize_text(str(row_label))
        norm_col = self._normalize_text(str(col_label))
        
        # Get potential row matches
        row_matches = self.row_index_map.get(norm_row, [])
        if not row_matches:
            # Fallback to fuzzy matching for rows
            row_matches = self._get_fuzzy_row_matches(norm_row)
        
        # Get potential column matches  
        col_matches = self.col_index_map.get(norm_col, [])
        if not col_matches:
            # Fallback to fuzzy matching for columns
            col_matches = self._get_fuzzy_col_matches(norm_col)
        
        # Check matches efficiently
        for table_idx, orig_row in row_matches:
            for table_col_idx, orig_col in col_matches:
                if table_idx == table_col_idx:  # Same table
                    total_searches += 1
                    try:
                        source_value = self.normalized_tables[table_idx].loc[orig_row, orig_col]
                        
                        # Check if both values are valid numbers
                        if (isinstance(source_value, (int, float)) and 
                            isinstance(normalized_value, (int, float)) and
                            not np.isnan(float(source_value)) and 
                            not np.isnan(float(normalized_value))):
                            
                            # Exact match check
                            if abs(float(source_value) - float(normalized_value)) < 0.01:
                                exact_matches += 1
                            
                            # Fuzzy match score
                            if abs(float(source_value)) > 0:
                                relative_diff = abs(float(normalized_value) - float(source_value)) / abs(float(source_value))
                                similarity = max(0, 1 - relative_diff)
                                best_fuzzy_score = max(best_fuzzy_score, similarity)
                    except (ValueError, TypeError, KeyError):
                        continue
        
        exact_score = exact_matches / max(1, total_searches)
        return exact_score, best_fuzzy_score
    
    @lru_cache(maxsize=500)
    def _get_fuzzy_row_matches(self, norm_row):
        """Cached fuzzy matching for rows"""
        matches = []
        for norm_idx, table_indices in self.row_index_map.items():
            if fuzz.partial_ratio(norm_row, norm_idx) > 80:
                matches.extend(table_indices)
        return matches
    
    @lru_cache(maxsize=500)
    def _get_fuzzy_col_matches(self, norm_col):
        """Cached fuzzy matching for columns"""
        matches = []
        for norm_col_key, table_indices in self.col_index_map.items():
            if fuzz.partial_ratio(norm_col, norm_col_key) > 80:
                matches.extend(table_indices)
        return matches
    
    def _get_source_reliability_score_fast(self, normalized_value, row_label, col_label):
        """Fast source reliability calculation"""
        confirming_sources = 0
        
        # Ensure normalized_value is numeric
        if not isinstance(normalized_value, (int, float)):
            try:
                normalized_value = float(normalized_value)
            except (ValueError, TypeError):
                return 0.0
                
        if np.isnan(normalized_value):
            return 0.0
        
        # Use pre-computed matches
        norm_row = self._normalize_text(str(row_label))
        norm_col = self._normalize_text(str(col_label))
        
        row_matches = self.row_index_map.get(norm_row, [])
        col_matches = self.col_index_map.get(norm_col, [])
        
        for table_idx, orig_row in row_matches:
            for table_col_idx, orig_col in col_matches:
                if table_idx == table_col_idx:
                    try:
                        source_value = self.normalized_tables[table_idx].loc[orig_row, orig_col]
                        
                        if isinstance(source_value, (int, float)) and not np.isnan(float(source_value)):
                            source_value = float(source_value)
                            if abs(source_value - normalized_value) / max(abs(normalized_value), 1) < 0.1:
                                confirming_sources += 1
                    except (ValueError, TypeError, KeyError):
                        continue
        
        return min(1.0, confirming_sources / 3.0)
    
    def _get_temporal_consistency_score_fast(self, normalized_value, row_label, col_label, normalized_result_df):
        """Vectorized temporal consistency calculation"""
        if col_label not in normalized_result_df.columns:
            return 0.5
        
        # Ensure normalized_value is numeric
        if not isinstance(normalized_value, (int, float)):
            try:
                normalized_value = float(normalized_value)
            except (ValueError, TypeError):
                return 0.5
                
        if np.isnan(normalized_value):
            return 0.5
        
        # Get all values for this row (vectorized)
        try:
            row_values = normalized_result_df.loc[row_label].values
            
            # Convert to numeric and filter out non-numeric values
            numeric_values = []
            for val in row_values:
                try:
                    if isinstance(val, (int, float)):
                        if not np.isnan(float(val)):
                            numeric_values.append(float(val))
                    else:
                        num_val = float(val)
                        if not np.isnan(num_val):
                            numeric_values.append(num_val)
                except (ValueError, TypeError):
                    continue
            
            if len(numeric_values) < 2:
                return 0.7
            
            # Fast statistical calculation
            other_values = [v for v in numeric_values if abs(v - normalized_value) > 0.01]
            if len(other_values) == 0:
                return 0.8
            
            mean_other = np.mean(other_values)
            std_other = np.std(other_values)
            
            if std_other == 0:
                return 0.8 if abs(normalized_value - mean_other) < abs(mean_other) * 0.1 else 0.3
            
            # Z-score based consistency
            z_score = abs((normalized_value - mean_other) / std_other)
            return max(0, 1 - z_score / 3.0)
            
        except Exception:
            return 0.5
    
    @lru_cache(maxsize=2000)
    def _normalize_financial_value(self, value):
        """Cached financial value normalization"""
        if pd.isna(value):
            return np.nan
        
        str_val = str(value).strip()
        if str_val == '' or str_val.upper() in ['N/A', 'NA', 'NULL', 'NONE']:
            return np.nan
        
        # Handle negative values in parentheses
        negative = '(' in str_val and ')' in str_val
        
        # Remove currency symbols, commas, and parentheses
        str_val = re.sub(r'[$,()]', '', str_val)
        
        try:
            numeric_val = float(str_val)
            return -numeric_val if negative else numeric_val
        except:
            return np.nan


