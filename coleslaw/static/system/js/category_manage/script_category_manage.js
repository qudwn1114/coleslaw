const categoryModal = document.getElementById('categoryModal');

const inputCategoryId = document.getElementById('categoryId');
const inputParentCategoryId = document.getElementById('parentCategoryId');
const inputCategoryType = document.getElementById('categoryType');
const inputCategoryNameKr = document.getElementById('categoryNameKr');
const inputCategoryNameEn = document.getElementById('categoryNameEn');

const btn_submit = document.getElementById("btn-submit");
const btn_edit = document.getElementById('btn-edit');

function getSubCateogryList(parent_id){
    $.ajax({
        type: "POST",
        url: "/system-manage/sub-category/",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            "parent_id" : parent_id
        },
        datatype: "JSON",
        success: function(data) {
            loadList(data.data, data.type);
        },
        error: function(error) {
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}


function selectLCategory(elem, id, name_kr, name_en){
    const mainCategory = document.querySelectorAll(".main-category");
    mainCategory.forEach(el => el.classList.remove('active'));
    elem.classList.add('active');

    const deleteLCategory = document.getElementById('deleteLCategory');
    const editLCategory = document.getElementById('editLCategory');

    deleteLCategory.style.display = 'block';
    editLCategory.style.display = 'block';

    deleteLCategory.setAttribute('data-main-id', id);
    editLCategory.setAttribute('data-main-id', id);
    editLCategory.setAttribute('data-category-name-kr', name_kr);
    editLCategory.setAttribute('data-category-name-en', name_en);

    const createSCategory = document.getElementById('createSCategory');
    createSCategory.setAttribute('data-parent-id', id);
    createSCategory.style.display = 'block';
    getSubCateogryList(id);
}

function selectSCategory(elem, id, name_kr, name_en){
    const subCategory = document.querySelectorAll(".sub-category");
    subCategory.forEach(el => el.classList.remove('active'));
    elem.classList.add('active');

    const deleteSCategory = document.getElementById('deleteSCategory');
    const editSCategory = document.getElementById('editSCategory');

    deleteSCategory.style.display = 'block';
    editSCategory.style.display = 'block';

    deleteSCategory.setAttribute('data-sub-id', id);
    editSCategory.setAttribute('data-sub-id', id);
    editSCategory.setAttribute('data-category-name-kr', name_kr);
    editSCategory.setAttribute('data-category-name-en', name_en);
}


// 모달 열릴 때 폼 초기화 및 데이터 넘기기
categoryModal.addEventListener('show.bs.modal', function (event) {
    $(this).find('form').trigger('reset');
    const button = event.relatedTarget
    // 카테고리 타입
    const categoryType = button.getAttribute('data-category-type');
    const modalType = button.getAttribute('data-modal-type');
    inputCategoryType.value = categoryType;
    if(categoryType == 'main'){
        // 모달 종류
        if(modalType == 'create'){
            btn_submit.style.display = 'block';
            btn_edit.style.display = 'none';
            inputCategoryNameKr.placeholder = '카테고리 한글 이름을 넣어주세요.';
            inputCategoryNameEn.placeholder = '카테고리 영문 이름을 넣어주세요.';
        }
        else if(modalType == 'edit'){
            btn_submit.style.display = 'none';
            btn_edit.style.display = 'block';
            inputCategoryId.value = button.getAttribute('data-main-id');
            inputCategoryNameKr.value = button.getAttribute('data-category-name-kr');
            inputCategoryNameKr.placeholder = button.getAttribute('data-category-name-kr');
            inputCategoryNameEn.value = button.getAttribute('data-category-name-en');
            inputCategoryNameEn.placeholder = button.getAttribute('data-category-name-en');
        }
    }
    else if(categoryType == 'sub'){
        if(modalType == 'create'){
            btn_submit.style.display = 'block';
            btn_edit.style.display = 'none';
            inputParentCategoryId.value = button.getAttribute('data-parent-id');
            inputCategoryNameKr.placeholder = '카테고리 한글 이름을 넣어주세요.';
            inputCategoryNameEn.placeholder = '카테고리 영문 이름을 넣어주세요.';
        }
        else if(modalType == 'edit'){
            btn_submit.style.display = 'none';
            btn_edit.style.display = 'block';
            inputCategoryId.value = button.getAttribute('data-sub-id');
            inputCategoryNameKr.value = button.getAttribute('data-category-name-kr');
            inputCategoryNameKr.placeholder = button.getAttribute('data-category-name-kr');
            inputCategoryNameEn.value = button.getAttribute('data-category-name-en');
            inputCategoryNameEn.placeholder = button.getAttribute('data-category-name-en');

        }
    }
    else{
        alert('모달창 오류..');
    }
});


//유효성 체크 함수
function validation(){
    if(inputCategoryType.value == ''){
        alert('카테고리 타입이 없습니다.');
        return false;
    }
    if(inputCategoryNameKr.value == ''){
        inputCategoryNameKr.focus();
        return false;
    }
    if(inputCategoryNameEn.value == ''){
        inputCategoryNameEn.focus();
        return false;
    }
    return true;
}

// 등록
btn_submit.addEventListener("click", () => {
    const data =new FormData(document.getElementById("data-form"));
    if(!validation()){
        return;
    }
    btn_submit.disabled=true;
    $.ajax({
        type: "POST",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: data,
        enctype: "multipart/form-data", //form data 설정
        processData: false, //프로세스 데이터 설정 : false 값을 해야 form data로 인식
        contentType: false, //헤더의 Content-Type을 설정 : false 값을 해야 form data로 인식
        success: function(data) {
            alert(data.message);
            btn_submit.disabled = false;
            loadList(data.data, data.type, data.id);
            $('#categoryModal').modal('hide');
        },
        error: function(error) {
            btn_submit.disabled = false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
});

// 수정
btn_edit.addEventListener("click", () => {
    const object = {};
    const formData =new FormData(document.getElementById("data-form"));
    formData.forEach(function(value, key){
        object[key] = value;
    });
    if(!validation()){
        return;
    }
    btn_edit.disabled=true;
    $.ajax({
        type: "PUT",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify(object),
        datatype: "JSON",
        success: function(data) {
            alert(data.message);
            btn_edit.disabled = false;
            loadList(data.data, data.type, data.id);
            $('#categoryModal').modal('hide');
        },
        error: function(error) {
            btn_edit.disabled = false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
});

//삭제
function deleteCategory(elem){
    let data;
    let categoryType;
    if(elem.getAttribute('data-main-id')){
        data = {
            'categoryType' : 'main',
            'categoryId' : elem.getAttribute('data-main-id')
        };
        categoryType = 'main';
    }
    else if(elem.getAttribute('data-sub-id')){
        data = {
            'categoryType' : 'sub',
            'categoryId' : elem.getAttribute('data-sub-id')
        };
        categoryType = 'sub';
    }
    else{
        return;
    }
    if (!confirm("정말 삭제하시겠습니까?")) {
        return;
    }
    elem.disabled = true;
    $.ajax({
        type: "DELETE",
        url: "",
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify(data),
        datatype: "JSON",
        success: function(data) {
            alert(data.message);
            elem.disabled = false;
            loadList(data.data, categoryType);
            $('#categoryModal').modal('hide');
        },
        error: function(error) {
            elem.disabled = false;
            if(error.status == 401){
                alert('로그인 해주세요.');
            }
            else if(error.status == 403){
                alert('권한이 없습니다!');
            }
            else{
                alert(error.status + JSON.stringify(error.responseJSON));
            }
        },
    });
}

function loadList(data, type, id){
    let x;
    let kr;
    let en;
    clearList(type)
    if(type == 'main'){
        if(data.length > 0){
            for(let i=0; i<data.length; i++){
                let a = document.createElement("a");
                if(data[i].id==id){
                    x = a;
                    kr = data[i].name_kr;
                    en = data[i].name_en;
                }
                a.classList.add("main-category", "list-group-item", "list-group-item-action");
                a.setAttribute("onClick", `selectLCategory(this, ${data[i].id}, '${data[i].name_kr}', '${data[i].name_en}')`);
                let textNode = document.createTextNode(data[i].name_kr);
                a.appendChild(textNode);
                a.href="javascript:;";
                document.getElementById('list-main-category').appendChild(a);
            }
            if(typeof id != 'undefined'){
                selectLCategory(x, id, kr, en);
                x.scrollIntoView();
            }
            else{
                const deleteLCategory = document.getElementById('deleteLCategory');
                const editLCategory = document.getElementById('editLCategory');
            
                deleteLCategory.style.display = 'none';
                editLCategory.style.display = 'none';
            }
        }
        else{
            const deleteLCategory = document.getElementById('deleteLCategory');
            const editLCategory = document.getElementById('editLCategory');
        
            deleteLCategory.style.display = 'none';
            editLCategory.style.display = 'none';
            
            let a = document.createElement("a");
            let textNode = document.createTextNode('데이터 등록해주세요.');
            a.appendChild(textNode);
            document.getElementById('list-main-category').appendChild(a);
        }
    }
    else if(type == 'sub'){
        if(data.length > 0){
            for(let i=0; i<data.length; i++){
                let a = document.createElement("a");
                if(data[i].id==id){
                    x = a;
                    kr = data[i].name_kr;
                    en = data[i].name_en;
                }
                a.classList.add("sub-category", "list-group-item", "list-group-item-action");
                a.setAttribute("onClick", `selectSCategory(this, ${data[i].id}, '${data[i].name_kr}', '${data[i].name_en}')`);
                a.href="javascript:;";
                let textNode = document.createTextNode(data[i].name_kr);
                a.appendChild(textNode);
                document.getElementById('list-sub-category').appendChild(a);
            }
            if(typeof id != 'undefined'){
                selectSCategory(x, id, kr, en);
                x.scrollIntoView();
            }
            else{
                const deleteSCategory = document.getElementById('deleteSCategory');
                const editSCategory = document.getElementById('editSCategory');
            
                deleteSCategory.style.display = 'none';
                editSCategory.style.display = 'none';
            }
        }
        else{
            const deleteSCategory = document.getElementById('deleteSCategory');
            const editSCategory = document.getElementById('editSCategory');
        
            deleteSCategory.style.display = 'none';
            editSCategory.style.display = 'none';

            let a = document.createElement("a");
            let textNode = document.createTextNode('데이터 등록해주세요.');
            a.appendChild(textNode);
            document.getElementById('list-sub-category').appendChild(a);
        }
    }
    else{
        return false;
    }
}


function clearList(type){
    if(type == 'main'){
        let div = document.getElementById('list-main-category');
        while(div.hasChildNodes()){
            div.removeChild(div.firstChild);
        }
    }
    else if(type == 'sub'){
        let div = document.getElementById('list-sub-category');
        while(div.hasChildNodes()){
            div.removeChild(div.firstChild);
        }
    }
    else{
        return false;
    }
}