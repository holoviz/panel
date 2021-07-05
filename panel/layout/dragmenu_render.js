function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    el = elmnt.getElementsByTagName('span')[0];
    if (el){
        el.onmousedown = dragMouseDown;
    } else {
        el.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        console.log('dragging');
        e = e || window.event;
        e.preventDefault();
        elmnt.style.top = e.clientY - 25 + 'px';
        elmnt.style.left = e.clientX -20 + 'px';
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

dragElement(drag_content);

drag_content.style.background_color = data.background_color
drag_content.style.visibility = 'hidden'

if(data.theme ==='dark'){drag_title.className = 'drag-handle-dark';}

 setTimeout(   function(){

if(data.position ==='out'){
    bcr  = drag_menu.getBoundingClientRect()
    bcr_content = drag_content.getBoundingClientRect()
    w = window.innerWidth
    h = window.innerHeight

    if(data.orientation ==='bl'){
        drag_content.style.left = String(bcr.left - bcr_content.width) +'px';
    }
    if(data.orientation ==='br'){
        drag_content.style.left = String(bcr.right) +'px';
    }
    if(data.orientation ==='tl'){
        drag_content.style.left = String(bcr.left - bcr_content.width) +'px';
        drag_content.style.top = String(bcr.top- bcr_content.height) +'px';
    }
    if(data.orientation ==='tr'){
        drag_content.style.left = String(bcr.right) +'px';
        drag_content.style.top = String(bcr.top- bcr_content.height) +'px';
    }
}

if(data.position ==='in'){
    bcr  = drag_menu.getBoundingClientRect()
    bcr_content = drag_content.getBoundingClientRect()
    w = window.innerWidth
    h = window.innerHeight

    if(data.orientation ==='bl'){
        console.log(bcr, bcr_content,bcr.bottom,bcr_content.height )
        drag_content.style.top = String(bcr.bottom - bcr_content.height) +'px';
    }
    if(data.orientation ==='br'){
        drag_content.style.top = String(bcr.bottom - bcr_content.height) +'px';
        drag_content.style.left = String(bcr.right - bcr_content.width) +'px';
    }
    if(data.orientation ==='tl'){
        drag_content.style.top = String(bcr.top) +'px';
    }
    if(data.orientation ==='tr'){
        drag_content.style.top = String(bcr.top) +'px';
        drag_content.style.left = String(bcr.right - bcr_content.width) +'px';
    }
}

 }, 50);
 