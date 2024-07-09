const btn_search = document.getElementById("btn-search");
const shop_name = document.getElementById('shop_name');


btn_search.addEventListener("click", () => {
    window.location.href = `?shop_name=${shop_name.value}`;
});

//유효성 체크 함수
function validation(){
    if(shop_name.value == ''){
        shop_name.focus();
        return false;
    }
    return true;
}

function enterkey() {
    if (window.event.keyCode == 13) {
        btn_search.click()
    }
}