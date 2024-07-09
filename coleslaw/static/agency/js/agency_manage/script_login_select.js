const btn_search = document.getElementById("btn-search");
const agency_name = document.getElementById('agency_name');


btn_search.addEventListener("click", () => {
    window.location.href = `?agency_name=${agency_name.value}`;
});

//유효성 체크 함수
function validation(){
    if(agency_name.value == ''){
        agency_name.focus();
        return false;
    }
    return true;
}

function enterkey() {
    if (window.event.keyCode == 13) {
        btn_search.click()
    }
}