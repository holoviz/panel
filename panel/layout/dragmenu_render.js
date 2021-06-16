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

//console.log(model.id, data, state, drag_menu) 
//console.log(data.color, drag_content.style)

drag_content.style.background_color = data.background_color
drag_content.style.visibility = 'hidden'

//console.log('zarpado')