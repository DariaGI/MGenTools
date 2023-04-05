function loadScript(url, callback) {
    const script = document.createElement('script');
    script.src = url;
    script.defer = true;
    script.onload = callback;
    document.body.appendChild(script);
}

loadScript('/static/scripts/requests.js', () => {
    console.log('Модуль запросов подключен');
})

document.getElementById('clsFormBtn').addEventListener('click', async () => {
    const formElem = document.getElementById('clsForm');
    const formData = new FormData(formElem);

    const resultsElem = document.getElementById('classificationResult');
    resultsElem.innerHTML = '<img width="50px" src="static/images/processing.gif">';

    const response = await request({
        method: 'POST',
        url: '/classify',
        data: formData
    })

    resultsElem.innerHTML = response;
    document.getElementById('resetBtn').style.display = 'block';
})


function reset() {
    document.getElementById('classificationResult').innerHTML = '';
}

// $(function () {
//     $('#clsFormBtn').click(function () {
//         var form_data = new FormData($('#clsForm')[0]);
//         console.log(form_data);
//         $('#classificationResult').html('<img width="50px" src="static/images/processing.gif">');
//         $.ajax({
//             type: 'POST',
//             url: '/classify',
//             data: form_data,
//             contentType: false,
//             cache: false,
//             processData: false,
//             success: function (data) {
//                 $('#classificationResult').html(data);
//             },
//         });
//     });
// });

// $.fn.reset = function () {
//     console.log("reseting");
//     var form_data = new FormData($('#resetForm')[0]);
//     $.ajax({
//         type: 'POST',
//         url: '/reset',
//         data: form_data,
//         contentType: false,
//         cache: false,
//         processData: false,
//         success: function (data) {
//             $('#classificationResult').html(data);
//         },
//     });
// };

$(function () {
    $('#countFormBtn').click(function () {
        var form_data = new FormData($('#countForm')[0]);
        $('#countSlide').html('<img width="50px" src="static/images/processing.gif">');
        $.ajax({
            type: 'POST',
            url: '/count',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                $('#countSlide').html(data);
            },
        });
    });
});
$(function () {
    $('#vslFormBtn').click(function () {
        var form_data = new FormData($('#vslForm')[0]);
        $('#vslSlide').html('<img width="50px" src="static/images/processing.gif">');
        $.ajax({
            type: 'POST',
            url: '/visualize',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                $('#vslSlide').html(data);
            },
        });
    });
});
$(function () {
    $('#uploadBreakdownBtn').click(function () {
        var form_data = new FormData($('#uploadBreakdown')[0]);
        $('#breakdownDisplay').html('<img width="50px" src="static/images/processing.gif">');
        $.ajax({
            type: 'POST',
            url: '/uploadBreakdown',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                $('#breakdownDisplay').html(data);
            },
        });
    });
});