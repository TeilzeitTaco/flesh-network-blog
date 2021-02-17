function set_background(file_name) {
    let file_path_url = `url("/static/images/${file_name}")`;
    document.body.style.setProperty("--global-background-image", file_path_url);
    localStorage.background = file_name;
}

(function remember_background() {
    let select = document.getElementById("background_select");
    select.onchange = () => set_background(select.value);
    if (localStorage.background)
        set_background(localStorage.background);

    select.value = localStorage.background;
})();

const PASSWORD_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
const PASSWORD_LENGTH = 32;

function generate_password() {
   let result = "";
   for (var i = 0; i < PASSWORD_LENGTH; i++)
      result += PASSWORD_CHARS.charAt(Math.floor(Math.random() * PASSWORD_CHARS.length));

   return result;
}

function get_password() {
    return localStorage.comment_password || (localStorage.comment_password = generate_password());
}

(function remember_form_data() {
    if (hidden_password_field = document.getElementById("hidden_password")) {
        hidden_password_field.value = get_password();

        let pseudonym_field = document.getElementById("pseudonym");
        pseudonym_field.value = localStorage.pseudonym || "";

        document.getElementById("submit").onclick = () => localStorage.pseudonym = pseudonym_field.value;
    }
})();


(function set_image_onclick() {
    let image_tags = document.getElementsByTagName("img");
    for (image_tag of image_tags) {
        let image_src = image_tag.src;
        image_tag.onclick = () => window.location.href = image_src;
    }
})();
