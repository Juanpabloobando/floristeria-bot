function getUserId() {
  let userId = localStorage.getItem("chat_user_id");

  if (!userId) {
    userId = "user_" + Math.random().toString(36).substring(2, 12);
    localStorage.setItem("chat_user_id", userId);
  }

  return userId;
}

async function sendMessage(customText = null) {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const userText = customText || input.value.trim();

  if (userText === "") return;

  const userMessage = document.createElement("div");
  userMessage.classList.add("message", "user");
  userMessage.textContent = userText;
  chatBox.appendChild(userMessage);

  input.value = "";

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ 
        text: userText,
        user_id: getUserId()
        })
    });

    const data = await response.json();

    const botMessage = document.createElement("div");
    botMessage.classList.add("message", "bot");
    botMessage.textContent = data.response;
    chatBox.appendChild(botMessage);

    if (data.options) {
      const optionsContainer = document.createElement("div");
      optionsContainer.classList.add("options-container");

      data.options.forEach(option => {
        const button = document.createElement("button");
        button.classList.add("option-button");
        button.textContent = option;
        button.onclick = () => sendMessage(option);
        optionsContainer.appendChild(button);
      });

      chatBox.appendChild(optionsContainer);
    }

    if (data.products) {
      const productsContainer = document.createElement("div");
      productsContainer.classList.add("products-container");

      data.products.forEach(product => {
        const card = document.createElement("div");
        card.classList.add("product-card");

        card.innerHTML = `
          <img src="${product.image}" alt="${product.name}" class="product-image">
          <div class="product-name">${product.name}</div>
          <div class="product-price">${product.price}</div>
          <div class="product-description">${product.description}</div>
        `;

        const button = document.createElement("button");
        button.classList.add("product-button");
        button.textContent = "Me interesa";
        button.onclick = () => sendMessage(product.name);

        card.appendChild(button);
        productsContainer.appendChild(card);
      });

      chatBox.appendChild(productsContainer);
    }

    chatBox.scrollTop = chatBox.scrollHeight;

  } catch (error) {
    const errorMessage = document.createElement("div");
    errorMessage.classList.add("message", "bot");
    errorMessage.textContent = "Error al conectar con el chatbot.";
    chatBox.appendChild(errorMessage);
  }
}