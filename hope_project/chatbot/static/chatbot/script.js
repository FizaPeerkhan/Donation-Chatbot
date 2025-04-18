function sendMessage() {
    let input = document.getElementById("userInput").value;
    let chatbox = document.getElementById("chatbox");

    // Display the user message in the chatbox
    chatbox.innerHTML += `<p class='user'>You: ${input}</p>`;

    // Send the message to the Django backend using fetch
    fetch(`/chatbot/get-response/?message=${input}`)
        .then(response => response.json())
        .then(data => {
            // Display the bot's response
            chatbox.innerHTML += `<p class='bot'>Bot: ${data.response}</p>`;
        });

    // Clear the input field
    document.getElementById("userInput").value = "";
}
