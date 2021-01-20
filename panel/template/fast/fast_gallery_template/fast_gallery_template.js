function hideCards(text) {
    text=text.toLowerCase();
    const cards = document.getElementsByTagName("li")
    for (const card of cards){
        if (text==="" || card.innerHTML.toLowerCase().includes(text)){
            card.style.display=""
        } else {card.style.display="none"}
    }
}
function toggleLightDarkTheme(){
    el=document.getElementById("body-design-provider")
    backgroundColor=el.getAttribute("background-color")
    if (backgroundColor === "#000000"){
        el.setAttribute("background-color", "#ffffff")
    } else {
        el.setAttribute("background-color", "#000000")
    }
}

