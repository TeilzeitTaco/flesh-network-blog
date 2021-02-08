function set_background(file_name) {
    let file_path_url = `url("/static/images/${file_name}")`;
    document.body.style.setProperty("--global-background-image", file_path_url);
    localStorage.background = file_name;
}


(() => {
    let select = document.getElementById("background_select");
    select.onchange = () => set_background(select.value);

    if (localStorage.background)
        set_background(localStorage.background);
})()
