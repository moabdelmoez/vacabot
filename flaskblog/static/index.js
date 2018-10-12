//console.clear();

var messageInput = document.querySelector('.chat__message-input');
var chatContainer = document.querySelector('#chat');
var messageButton = document.querySelector('.chat__message-button');


var input = document.getElementById("myinput");

// Execute a function when the user releases a key on the keyboard
input.addEventListener("keyup", function(event) {
    console.log("aaa")
  // Cancel the default action, if needed
  event.preventDefault();
  // Number 13 is the "Enter" key on the keyboard
  if (event.keyCode === 13) {
    // Trigger the button element with a click
    document.getElementById("mybutton").click();
  }
});

$('.starter').append('<strong>Jolia</strong> at <strong>' + moment().format('h:mm A') + '</strong>')

function submit_message(message) {
    $.post( "/send_message", {message: message}, handle_response);
    
    function handle_response(data) {
        let arr = data.message;
        console.log(arr)
        arr.forEach(element => {
            console.log(element)
            var chatItem1 = document.createElement('li');
            var chatAvatar1 = document.createElement('div');
            var chatContent1 = document.createElement('div');
            var chatMessage1 = document.createElement('div');
            var chatInfo1 = document.createElement('small');
            chatItem1.classList.add('chat__item');
            chatAvatar1.classList.add('chat__avatar');
            chatContent1.classList.add('chat__content');
            chatMessage1.classList.add('chat__message');
            chatInfo1.classList.add('chat__info');
            chatInfo1.innerHTML = '<strong>Jolia</strong> at <strong>' + moment().format('h:mm A') + '</strong>';
            chatAvatar1.style.backgroundImage = 'url(https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-0.3.5&amp;q=80&amp;fm=jpg&amp;crop=entropy&amp;cs=tinysrgb&amp;w=200&amp;fit=max&amp;s=707b9c33066bf8808c934c8ab394dff6)';
            chatContainer.appendChild(chatItem1);
            chatItem1.appendChild(chatAvatar1);
            chatItem1.appendChild(chatContent1);
            chatContent1.appendChild(chatMessage1);
            chatContent1.appendChild(chatInfo1);
            chatMessage1.innerHTML = element;
            chatContainer.scrollTop = chatContainer.scrollHeight;
        })
		$( ".dots" ).remove();
	
	}
	
}

var newMessage = function newMessage() {
    var  messageText = messageInput.value;
	
	var chatItem = document.createElement('li');
	var chatAvatar = document.createElement('div');
	var chatContent = document.createElement('div');
	var chatMessage = document.createElement('div');
	var chatInfo = document.createElement('small');
	chatItem.classList.add('chat__item', 'chat__item--agent');
	chatAvatar.classList.add('chat__avatar');
	chatContent.classList.add('chat__content');
	chatMessage.classList.add('chat__message');
    chatInfo.classList.add('chat__info');
    var my_username = $('#my-user').data().name;
	chatInfo.innerHTML =  "<strong>" + my_username + "</strong> at <strong>" + moment().format('h:mm A') + '</strong>';
	chatAvatar.style.backgroundImage = 'url(https://pbs.twimg.com/profile_images/943227488292962306/teiNNAiy.jpg)';
	chatContainer.appendChild(chatItem);
	chatItem.appendChild(chatAvatar);
	chatItem.appendChild(chatContent);
	chatContent.appendChild(chatMessage);
	chatContent.appendChild(chatInfo);
	chatMessage.innerHTML = messageText;
	chatContainer.scrollTop = chatContainer.scrollHeight;
	messageInput.value = '';
	var messageText2 = '...';
	var chatItem1 = document.createElement('li');
	var chatAvatar1 = document.createElement('div');
	var chatContent1 = document.createElement('div');
	var chatMessage1 = document.createElement('div');
	var chatInfo1 = document.createElement('small');
	chatItem1.classList.add('chat__item','dots');
	chatAvatar1.classList.add('chat__avatar');
	chatContent1.classList.add('chat__content');
	chatMessage1.classList.add('chat__message');
	chatInfo1.classList.add('chat__info');
	chatInfo1.innerHTML = '<strong>Jolia</strong> at <strong>' + moment().format('h:mm A') + '</strong>';
	chatAvatar1.style.backgroundImage = 'url(https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-0.3.5&amp;q=80&amp;fm=jpg&amp;crop=entropy&amp;cs=tinysrgb&amp;w=200&amp;fit=max&amp;s=707b9c33066bf8808c934c8ab394dff6)';
	chatContainer.appendChild(chatItem1);
	chatItem1.appendChild(chatAvatar1);
	chatItem1.appendChild(chatContent1);
	chatContent1.appendChild(chatMessage1);
	chatContent1.appendChild(chatInfo1);
	chatMessage1.innerHTML = messageText2;
	chatContainer.scrollTop = chatContainer.scrollHeight;
	submit_message(messageText)
	





};



messageInput.addEventListener("keydown", function (e) {
	if (e.keyCode == 13 && e.ctrlKey) {
		newMessage();
		

	}
});


var clearMessage = function clearMessage() {
	messageInput.value = '';
};
