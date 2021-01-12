function create_editor(id, jme){
    element = document.getElementById(id)
    element.jsmeApplet =  new JSApplet.JSME(id, "600px", "440px", {
        //optional parameters
        "options": "query,hydrogens,fullScreenIcon",
        "jme": startingStructure // JME mol format
    });
}
