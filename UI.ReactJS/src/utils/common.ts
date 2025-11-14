export function convertUpperCase(string: string) {
    if (string.toLowerCase() === 'pdf') {
        return string.toUpperCase();
    } else {
        return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
    }
}

export function convertTimestamp(timestamp: string, onlyDate: boolean = false) {
    const date = new Date(timestamp);
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); 
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return onlyDate ? `${day}/${month}/${year}` : `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
}