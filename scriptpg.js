function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].style.backgroundColor = "";
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.style.backgroundColor = "#007acc";
}

document.getElementById('Inputs').style.display = "block";

function submitGrammar() {
    const nonTerminals = document.getElementById('nonTerminals').value.split(',');
    const terminals = document.getElementById('terminals').value.split(',');
    const productions = document.getElementById('productions').value;

    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nonTerminals, terminals, productions })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('firstOutput').innerText = 'FIRST: ' + JSON.stringify(data.first);
        document.getElementById('followOutput').innerText = 'FOLLOW: ' + JSON.stringify(data.follow);
        openTab(null, 'Output');
    });
}
