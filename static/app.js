const uploadPhotoBtn =
    document.getElementById("uploadPhotoBtn");

const foodInput =
    document.getElementById("foodInput");


uploadPhotoBtn.addEventListener("click", function () {

    foodInput.click();

});
// for Image preview after upload
foodInput.addEventListener("change", function () {

    if (this.files[0]) {
        document.getElementById("foodImage").src =
            URL.createObjectURL(this.files[0]);
    }

});

// tabs button activate 

const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(function (button) {
    button.addEventListener("click", function () {

        tabButtons.forEach(function (btn) {
            btn.classList.remove("active");
        });

        tabContents.forEach(function (content) {
            content.classList.remove("active");
        });

        button.classList.add("active");

        document
            .getElementById(button.dataset.tab)
            .classList.add("active");
    });
});