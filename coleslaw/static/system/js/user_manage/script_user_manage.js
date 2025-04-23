function xlsxDownload(){
    if(!confirm("엑셀저장하시겠습니까?")){
        return false;
    }
    if(window.location.search){
        console.log(window.location.search);
        strurl = window.location.pathname + window.location.search;
        window.location.href= strurl + '&excel=excel';
    }
    else{
        console.log(window.location.search);
        strurl = window.location.pathname;
        window.location.href= strurl + '?excel=excel';
    }
}




function changeActive(id, checkbox){
    if(checkbox.checked){
        var text = "활성";
        var status = 1;
    }else{
        var text = "비활성";
        var status = 0;
    }
    if(!confirm(`${text} 하시겠습니까?`)){
        if(text == "활성"){
            checkbox.parentElement.classList.remove("btn-primary");
            checkbox.parentElement.classList.add("btn-light","off");
        }else{
            checkbox.parentElement.classList.remove("btn-light", "off");
            checkbox.parentElement.classList.add("btn-primary");
        }
        checkbox.checked = !checkbox.checked
        return false;
    }

    $.ajax({
        type: "PUT",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify({ 
            "type" : "ACTIVE",
            "user_id" : id,
            "is_active" : status
        }),
        datatype: "JSON",
        success: function(data) {
            location.reload(true);
        },
        error: function(error) {
            if(error.status == 401){
                customAlert('로그인 해주세요.');
            }
            else if(error.status == 403){
                customAlert('권한이 없습니다!');
            }
            else{
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
            if(checkbox.checked){
                checkbox.parentElement.classList.remove("btn-primary");
                checkbox.parentElement.classList.add("btn-light","off");
            }else{
                checkbox.parentElement.classList.remove("btn-light", "off");
                checkbox.parentElement.classList.add("btn-primary");
            }
            checkbox.checked = !checkbox.checked
        },
    });
}


function setAdmin(id, elem){
    if (!confirm("관리자 지정을 수정하시겠습니까?")) {
        location.reload();
        return;
    }
    let data = {
        type : "SUPERUSER",
        user_id : id
    };
    elem.disabled=true;
    $.ajax({
        type: "PUT",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify(data),
        datatype: "JSON",
        success: function(data) {
            location.reload();
        },
        error: function(error) {
            elem.disabled=false;
            if(error.status == 401){
                customAlert('로그인 해주세요.');
            }
            else if(error.status == 403){
                customAlert('권한이 없습니다!');
            }
            else{
                location.reload();
                customAlert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}