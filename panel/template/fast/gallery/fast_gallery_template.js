function setParamsFromSearch(text){
    const params = new URLSearchParams(location.search);
    if (text===""){
        params.delete("search")
    } else {
        params.set('search', text);
    }
    window.history.replaceState({}, '', `${location.pathname}?${params}`);
}
function hideCards(text) {
  text=text.toLowerCase();
  const cards = document.getElementsByTagName("li")
  for (const card of cards){
      if (text==="" || card.innerHTML.toLowerCase().includes(text)){
          card.style.display=""
      } else {card.style.display="none"}
  }

  setParamsFromSearch(text)
}
function toggleLightDarkTheme(){
    el=document.getElementById("body-design-provider")
    const switchEl = document.getElementById("theme-switch")
    const params = new URLSearchParams(location.search);

    if (switchEl.checked){
        el.setAttribute("background-color", "#ffffff")
        params.set('theme', "default");
    } else {
        el.setAttribute("background-color", "#000000")
        params.set('theme', "dark");
    }
    window.history.replaceState({}, '', `${location.pathname}?${params}`);
}
function setSwitchFromParams(){
    const params = new URLSearchParams(window.location.search)
    if (params.has('theme')){
        const theme = params.get('theme')
        const switchEl = document.getElementById("theme-switch")
        if (theme==='dark'){
            switchEl.checked=false
        } else {
            switchEl.checked=true
        }
        toggleLightDarkTheme()
    }
}
function setSearchFromParams(){
    const params = new URLSearchParams(window.location.search)
    if (params.has('search')){
        const search = params.get('search')
        const searchEl = document.getElementById("search-input")
        searchEl.value = search
        hideCards(search)
    }
}

