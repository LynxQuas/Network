const edit_btn = document.querySelectorAll(".btn_edit");
const modal_container = document.querySelector(".modal-container");
const close_btn = document.querySelector(".btn_close");
const save_btn = document.querySelector(".btn_save");

const edit_input = document.querySelector(".edit_input");
const edit_form = document.querySelector("#edit_form");

const react_btn = document.querySelectorAll(".reaction");
const alert_warning = document.querySelector(".alert-warning");

function hide_alert() {
    alert_warning.style.display = "none";
}

function show_alert(message) {
    alert_warning.textContent = message;
    alert_warning.style.display = "block";
}

function fetch_and_upload_content(url, options, callback) {
    fetch(url, options)
        .then((response) => response.json())
        .then(callback);
}

function edit_handler(event) {
    hide_alert();
    modal_container.style.display = "flex";
    const postId = event.target.dataset.postId;

    fetch_and_upload_content(`/posts/${postId}`, null, (post) => {
        edit_input.value = post.content;
        edit_form.setAttribute("data-post-id", post.id);
    });
}

function save_edit_handler(event) {
    hide_alert();
    modal_container.style.display = "none";
    const id = edit_form.dataset.postId;

    const csrfToken = edit_form.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;

    const option = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
            content: edit_input.value,
        }),
    };

    const callback = (updated_post) => {
        const content_container = document.querySelectorAll(".content");
        content_container.forEach((content) => {
            if (content.dataset.contentId !== id) return;
            content.textContent = updated_post.content;
        });
    };

    fetch_and_upload_content(`/posts/${id}`, option, callback);
}
react_btn.forEach((react) => {
    react.addEventListener("click", (event) => {
        const current_post_id = event.target.dataset.reaction;
        const current_user = event.target.dataset.currentUser;

        if (current_user === "AnonymousUser") return;

        // options for fetching data.
        const csrfToken = edit_form.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;

        const option = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({
                likes: current_user,
            }),
        };

        // updated the content.
        const callback = (result) => {
            document.querySelector(".alert-warning").style.display = "none";
            if (result.error) {
                document.querySelector(".alert-warning").textContent =
                    result.error;
                document.querySelector(".alert-warning").style.display =
                    "block";
            } else {
                event.target.children[0].textContent = result.post.likes.length;
            }
        };

        // get the data and update the content.
        fetch_and_upload_content(`/posts/${current_post_id}`, option, callback);
    });
});

// Event Listeners
close_btn.onclick = () => (modal_container.style.display = "none");
edit_btn.forEach((btn) => (btn.onclick = edit_handler));
save_btn.onclick = save_edit_handler;
