const btn_search = document.getElementById("btn-search");
const shop_name_kr = document.getElementById('shop_name_kr');


btn_search.addEventListener("click", () => {
    window.location.href = `?shop_name_kr=${shop_name_kr.value}`;
});

//유효성 체크 함수
function validation(){
    if(shop_name_kr.value == ''){
        shop_name_kr.focus();
        return false;
    }
    return true;
}

function enterkey() {
    if (window.event.keyCode == 13) {
        btn_search.click()
    }
}