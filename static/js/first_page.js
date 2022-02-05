function F(){
            window.location.href = 'registration.html';
           }
function X(){
    login_in_db = (document.getElementById('login').value);
    if (login_in_db === "Vladragone"){
        window.location.href = 'password_input.html';
    } else{
        reg = document.getElementById('go_to_reg1');
        reg.style.visibility = "visible";
        reg = document.getElementById('go_to_reg');
        reg.style.visibility = "visible";
        
        }
    }
