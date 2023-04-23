var checkboxClick = false;

function chooseAll(source) {
    if (source.name == 'allCategories') {
        var data_name = 'categories';
        var tag_name = 'name';
        var ctgButtons = document.getElementsByName("ctgLabel");

        for (let ctgButton of ctgButtons) {
            ctgButton.className = 'btn btn1';
            ctgButton.classList.add(source.checked ? 'btn-secondary' : ' btn-outline-secondary')
        }
    }
    else {
        if (source.name == 'allSystems') {
            var data_name = 'systems';
            var tag_name = 'name';
            var ctgButtons = document.getElementsByName("stmsLabel");
            for (i = 0; i < ctgButtons.length; i++) {
                if (source.checked) {
                    ctgButtons[i].className = 'btn btn-secondary btn2';
                }
                else {
                    ctgButtons[i].className = 'btn btn-outline-secondary btn2';
                }
            }
        }
        else {
            checkboxClick = true;
            var data_name = 'system' + source.name;
            var tag_name = 'data-name';
        }
    }

    checkboxes = document.querySelectorAll("[" + tag_name + "=" + data_name + "]");
    for (i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = source.checked;
    }
}

function show(source) {
    if (!checkboxClick) {
        // img = source.querySelectorAll('img')[0];
        img = source.querySelector('img');
        nm = 'system' + source.getAttribute('name');
        // systems = document.querySelectorAll("[data-name=" + nm + "]");
        systems = document.querySelectorAll(`[data-name=${nm}]`);
        systemsBlock = systems[0].parentElement;
        if (systemsBlock.style.display == 'none' || systemsBlock.style.display == '') {
            systemsBlock.style.display = 'block';
            img.src = "static/images/arrow_up.png";
        }
        else {
            systemsBlock.style.display = 'none';
            img.src = "static/images/arrow_down.png";
        }
    }
    else
        checkboxClick = false;
}

function changeBtn(source) {
    if (source.classList.contains('btn-outline-secondary')) {
        source.classList.remove('btn-outline-secondary');
        source.classList.add('btn-secondary');
    } 
    else if (source.classList.contains('btn-secondary')) {
        source.classList.remove('btn-secondary');
        source.classList.add('btn-outline-secondary');
    }
}

function showElement(selector) {
    document.querySelector(selector).classList.toggle('d-none');
}

const unifracSelect = document.querySelector('select[name="unifrac"]');

unifracSelect.addEventListener('change', () => {
    const selected = unifracSelect.options[unifracSelect.selectedIndex];
    document.querySelector('.unifrac-data').style.display = selected.value === 'none' ? 'none' : 'block';
})

const clusterMethodSelect = document.getElementById('clusterMethod');

clusterMethodSelect.addEventListener('change', () => {
    const selected = clusterMethodSelect.options[clusterMethodSelect.selectedIndex];
    const target = selected.getAttribute('data-target');
    if (selected.value === 'none') {
        document.querySelectorAll('.togglable').forEach(elem => elem.classList.add('d-none'));
    }
    if (target === null) return;
    document.querySelectorAll('.togglable').forEach(elem => elem.classList.add('d-none'));
    document.querySelector(target).classList.toggle('d-none');
});