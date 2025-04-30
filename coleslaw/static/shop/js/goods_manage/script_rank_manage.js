const main_category = document.getElementById("main_category");
const sub_category = document.getElementById("sub_category");

let main_category_list = new Array();
let sub_category_list = new Array();

window.onload = function(){
    // 카테고리 초기화
    $.ajax({
        type: "POST",
        headers: {
            'X-CSRFToken': csrftoken
        },
        url: `/shop-manage/${shop_id}/category/`,
        success: function(data) {
            main_category_list = data.main_category_list;
            sub_category_list = data.sub_category_list;
            setCategory("main", main_category_list);
            
        },
        error: function(error) {
            customAlert(error.status + error.responseJSON.message);
        },
    });
}

function setCategory(type, arr){
    let $oSelect;
    if(type=='main'){
        $oSelect = $('#main_category');
    }
    else if(type=='sub'){
        $oSelect = $('#sub_category');
    }
    else{
        return;
    }
    $oSelect.empty();
    if(arr.length == 0){
        return;
    }
    $oSelect.removeAttr("disabled");
    for(let i=0; i<arr.length; i++){
        $oSelect.append(new Option(arr[i].name_kr , arr[i].id, false, false));
    }
    $oSelect.selectpicker('refresh');
}

function selectCategory(type, id){
    let $sSelect = $('#sub_category');

    let filterArr = new Array();

    if(type=='main'){
        $sSelect.empty();
        $sSelect.attr("disabled", true);
        $sSelect.selectpicker('refresh');

        filterArr = sub_category_list.filter(function(elem){
            return elem.parent_id == id;
        });
        setCategory("sub", filterArr);
        sub_category.focus();
        
    }
    else{
        sub_category_id = id;
        getGoodsList(sub_category_id);
        return;
    }
}

function getGoodsList(sub_category_id){
    $.ajax({
        type: "GET",
        url: `/shop-manage/${shop_id}/rank-goods/${sub_category_id}/?rank_type=${rank_type}`,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(data) {
            setGoodsList(data.goods_list);
        },
        error: function(error) {
            customAlert('로드 실패: ' + error.status);
        }
    });
}

function setGoodsList(goods_list) {
    const container = document.querySelector('.goods-list-container');
    container.innerHTML = ''; // 초기화

    if (!goods_list || goods_list.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">해당 카테고리에 등록된 상품이 없습니다.</p>';
        return;
    }

    const ul = document.createElement('ul');
    ul.id = 'sortable-goods';
    ul.className = 'list-group';

    goods_list.forEach(item => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.setAttribute('data-id', item.id);
        li.setAttribute('style', 'user-select: none;');
        li.setAttribute('style', 'cursor: grab;');
        li.innerHTML = `
            <i class="bi bi-list" style="cursor: move;"></i>
            <span>${item.name_kr} [${numberWithCommas(item.sale_price)}원]</span>
        `;
        ul.appendChild(li);
    });
    container.appendChild(ul);
    
    $('#sortable-goods').sortable({
        animation: 150,  // 숫자가 클수록 느리게, 단위: ms
        onEnd: function(evt) {
            saveOrder();  // 드래그 후 순서 저장 함수 호출
        }
    });
}


// 순서 저장 함수
function saveOrder() {
    const items = document.querySelectorAll('#sortable-goods li');
    const orderData = [];

    items.forEach((li, index) => {
        orderData.push({
            id: li.getAttribute('data-id'),
            rank: index + 1
        });
    });
    // 순서 변경 후 바로 서버에 저장
    $.ajax({
        type: "POST",
        url: `/shop-manage/${shop_id}/rank-goods/${sub_category_id}/update/?rank_type=${rank_type}`,  // 서버에 맞는 URL로 수정
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify({ order: orderData }),
        contentType: 'application/json',
        success: function(response) {
            console.log('순서가 성공적으로 저장되었습니다!');
        },
        error: function(error) {
            customAlert('저장 실패: ' + error.status);
        }
    });
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}