from passlib.context import CryptContext
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate hash for a password"""
    return pwd_context.hash(password)

def generate_random_password(length: int = 6) -> str:
    """
    Generate a random password with specified length.
    
    The password will contain:
    - At least one uppercase letter
    - At least one lowercase letter  
    - At least one digit
    - Remaining characters from alphanumeric set
    
    Args:
        length (int): Length of password to generate (minimum 6)
        
    Returns:
        str: Generated random password
    """
    if length < 6:
        length = 6
    
    # Ensure we have at least one of each required type
    password_chars = [
        secrets.choice(string.ascii_uppercase),  # At least one uppercase
        secrets.choice(string.ascii_lowercase),  # At least one lowercase  
        secrets.choice(string.digits),           # At least one digit
    ]
    
    # Fill the rest with random alphanumeric characters
    remaining_length = length - len(password_chars)
    all_chars = string.ascii_letters + string.digits
    password_chars.extend(secrets.choice(all_chars) for _ in range(remaining_length))
    
    # Shuffle the password to randomize character positions
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)
