function page(num){
    let urlParams = new URLSearchParams(window.location.search);
    urlParams.set('page', num);
    window.location.href = `?${urlParams.toString()}`;
}