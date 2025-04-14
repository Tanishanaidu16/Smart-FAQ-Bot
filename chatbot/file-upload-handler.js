document.getElementById('fileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
 
    // Ensure it's a JavaScript file
    if (file && file.name.endsWith('.js')) {
        const reader = new FileReader();
       
        reader.onload = function(e) {
            const scriptContent = e.target.result;
 
            // Dynamically create a <script> element and add the uploaded script content to it
            const script = document.createElement('script');
            script.textContent = scriptContent;
            document.body.appendChild(script);  // This will execute the uploaded JavaScript
 
            // Show the chatbot regardless of the content of the uploaded file
            showChatbot();  // Display the chatbot after the script is loaded
        };
 
        reader.readAsText(file);  // Read the file content as text
    } else {
        alert('Please select a valid JavaScript file.');
    }
});
 
// Function to display the chatbot
function showChatbot() {
    console.log('Initializing chatbot...');
 
    // Create the "Chat" button
    const chatButton = document.createElement('button');
    chatButton.textContent = 'Chat';
    chatButton.style.position = 'fixed';
    chatButton.style.bottom = '20px';
    chatButton.style.right = '20px';
    chatButton.style.padding = '12px 18px';
    chatButton.style.backgroundColor = '#25d366'; // Green button (like in the image)
    chatButton.style.color = '#fff';
    chatButton.style.border = 'none';
    chatButton.style.borderRadius = '50%';
    chatButton.style.fontSize = '18px';
    chatButton.style.cursor = 'pointer';
    chatButton.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    document.body.appendChild(chatButton);
 
    // Create the chatbot popup window
    const chatPopup = document.createElement('div');
    chatPopup.style.position = 'fixed';
    chatPopup.style.bottom = '70px';
    chatPopup.style.right = '20px';
    chatPopup.style.width = '350px';
    chatPopup.style.height = '450px';
    chatPopup.style.backgroundColor = '#fff';
    chatPopup.style.borderRadius = '10px';
    chatPopup.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.1)';
    chatPopup.style.display = 'none';  // Initially hidden
    chatPopup.style.flexDirection = 'column';
    document.body.appendChild(chatPopup);
 
    // Add header to the popup
    const chatHeader = document.createElement('div');
    chatHeader.style.backgroundColor = '#25d366';  // Same green header color
    chatHeader.style.color = '#fff';
    chatHeader.style.padding = '15px';
    chatHeader.style.fontSize = '16px';
    chatHeader.style.fontWeight = 'bold';
    chatHeader.style.display = 'flex';
    chatHeader.style.justifyContent = 'space-between';
    chatHeader.innerHTML = `
        <span>Hi! I'm Apollo, an AI Assistant.</span>
        <button class="close-btn" style="background: none; border: none; color: white; font-size: 20px; cursor: pointer;">×</button>
    `;
    chatPopup.appendChild(chatHeader);
 
    // Add body to the popup
    const chatBody = document.createElement('div');
    chatBody.style.padding = '15px';
    chatBody.style.fontSize = '14px';
    chatBody.style.color = '#333';
    chatBody.style.overflowY = 'auto';
    chatBody.innerHTML = `
        <div class="chat-message"><span>What is tawk.to?</span></div>
        <div class="chat-message"><span>Why should I choose tawk.to?</span></div>
        <div class="chat-message"><span>How do I set up an AI Chatbot?</span></div>
        <div class="chat-message"><span>I have a different question</span></div>
    `;
    chatPopup.appendChild(chatBody);
 
    // Add close button functionality
    const closeBtn = chatHeader.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => {
        chatPopup.style.display = 'none';
    });
 
    // Toggle the chatbot popup on button click
    chatButton.addEventListener('click', () => {
        chatPopup.style.display = chatPopup.style.display === 'none' ? 'flex' : 'none';
    });
}