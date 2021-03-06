// /static/custom.js

var dateWithouthSecond = new Date();
dateWithouthSecond.toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'});

function submit_message(message) {
    $.post( "/send_message", {message: message}, handle_response);

    function handle_response(data) {
      // append the bot repsonse to the div
      let arr = data.message
      arr.forEach(element => {
        $('.chat-container').append(`
        <div class="chat-message col-md-5 offset-md-7 bot-message">
            ${element}
        </div>
        <p align="right"><small>${new Date().toLocaleTimeString()}</small></p>
        `)
      });
      
      // remove the loading indicator
      $( "#loading" ).remove();
      scrollToDown();

    }
}

function scrollToDown() {
     var objDiv = document.getElementById("my-chat");
     objDiv.scrollTop = objDiv.scrollHeight;
}
// /static/custom.js

$('#target').on('submit', function(e){
    e.preventDefault();
    const input_message = $('#input_message').val()
    // return if the user does not enter any text
    if (!input_message) {
      return
    }

    $('.chat-container').append(`
        <div class="chat-message col-md-5 human-message">
            ${input_message}
        </div>
        <p><small>${new Date().toLocaleTimeString()}</small></p>
    `)

    // loading 
    $('.chat-container').append(`
        <div class="chat-message text-center col-md-2 offset-md-10 bot-message" id="loading">
            <b>...</b>
        </div>
    `)

    // clear the text input 
    $('#input_message').val('')
    scrollToDown();
    // send the message
    submit_message(input_message)
});
