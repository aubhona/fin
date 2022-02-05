
function X(){
    password_correct = (document.getElementById('text').value);
    if (password_correct === '123'){
        window.location.href = 'welcome.html';
    } else{
        er = document.getElementById('Error');
        er.style.visibility = "visible";
    }
}

