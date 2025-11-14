import React from 'react';
import { Link } from 'react-router-dom';
import './ForbiddenPage.css';

const ForbiddenPage: React.FC = () => {
  return (
    <div className="forbidden-page">
      <h1>403</h1>
      <h2>Forbidden</h2>
      <p>Sorry, you do not have permission to access this page.</p>
      <Link to="/" className="btn-home">Back</Link>
    </div>
  );
};

export default ForbiddenPage;