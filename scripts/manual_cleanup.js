// Manual cleanup script for malformed HTML patterns
// Run this in the browser developer console after uploading a document

function cleanMalformedHTML() {
    console.log('🧹 Starting manual cleanup of malformed HTML patterns...');
    
    // Find all elements that might contain malformed HTML
    const documentContent = document.querySelector('.document-section');
    
    if (!documentContent) {
        console.warn('Document section not found');
        return;
    }
    
    let cleaned = 0;
    
    // Method 1: Fix malformed text content
    function cleanTextNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            let originalText = node.textContent;
            
            // Check for the specific malformed pattern
            if (originalText.includes('="sentence-highlight"')) {
                console.log('🚨 Found malformed pattern:', originalText.substring(0, 100));
                
                // Extract just the actual text content
                let cleanText = originalText;
                
                // Remove the malformed HTML attributes
                cleanText = cleanText.replace(/=["'][^"']*["'][^>]*>/g, '');
                cleanText = cleanText.replace(/\s*(?:id|class|data-[\w-]+)\s*=\s*["'][^"']*["']/g, '');
                cleanText = cleanText.replace(/<\/?[^>]*>/g, '');
                cleanText = cleanText.trim();
                
                if (cleanText !== originalText) {
                    node.textContent = cleanText;
                    cleaned++;
                    console.log('✅ Cleaned text:', cleanText.substring(0, 50) + '...');
                }
            }
        }
    }
    
    // Method 2: Fix malformed HTML elements
    function cleanElement(element) {
        // Check innerHTML for malformed patterns
        if (element.innerHTML && element.innerHTML.includes('="sentence-highlight"')) {
            console.log('🚨 Found malformed HTML in element:', element.tagName);
            
            let cleanHTML = element.innerHTML;
            cleanHTML = cleanHTML.replace(/=["'][^"']*sentence-highlight[^"']*["'][^>]*>/g, '');
            cleanHTML = cleanHTML.replace(/\s*(?:id|class|data-[\w-]+)\s*=\s*["'][^"']*["']/g, '');
            
            if (cleanHTML !== element.innerHTML) {
                element.innerHTML = cleanHTML;
                cleaned++;
                console.log('✅ Cleaned element HTML');
            }
        }
        
        // Check text content
        if (element.textContent && element.textContent.includes('="sentence-highlight"')) {
            let cleanText = element.textContent;
            cleanText = cleanText.replace(/=["'][^"']*["'][^>]*>/g, '');
            cleanText = cleanText.replace(/\s*(?:id|class|data-[\w-]+)\s*=\s*["'][^"']*["']/g, '');
            cleanText = cleanText.trim();
            
            if (cleanText !== element.textContent && element.children.length === 0) {
                element.textContent = cleanText;
                cleaned++;
                console.log('✅ Cleaned element text');
            }
        }
    }
    
    // Walk through all nodes
    function walkNodes(node) {
        cleanTextNode(node);
        
        if (node.nodeType === Node.ELEMENT_NODE) {
            cleanElement(node);
        }
        
        for (let child of node.childNodes) {
            walkNodes(child);
        }
    }
    
    walkNodes(documentContent);
    
    console.log(`✅ Cleanup complete! Fixed ${cleaned} malformed patterns.`);
    
    return cleaned;
}

// Auto-run the cleanup
const cleanedCount = cleanMalformedHTML();

if (cleanedCount > 0) {
    console.log('🎉 Malformed HTML patterns have been cleaned!');
} else {
    console.log('ℹ️ No malformed patterns found to clean.');
}