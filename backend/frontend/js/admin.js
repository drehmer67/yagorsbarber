const API = window.location.origin

function carregarAgenda(){

const data = document.getElementById("filtroData").value
const barbeiro = document.getElementById("filtroBarbeiro").value

fetch(`${API}/agendamentos`)
.then(res => res.json())
.then(lista => {

const container = document.getElementById("lista")
container.innerHTML = ""

lista
.filter(a => !data || a.data === data)
.filter(a => !barbeiro || a.barbeiro === barbeiro)
.forEach(a => {

const item = document.createElement("div")
item.className = "card-agendamento"

item.innerHTML = `
<h3>${a.nome}</h3>
<p>💈 ${a.barbeiro}</p>
<p>📅 ${a.data}</p>
<p>⏰ ${a.horario}</p>
<p>💰 R$ ${a.valor}</p>

<button onclick="cancelar('${a.nome}','${a.data}','${a.horario}')">
❌ Cancelar
</button>
`

container.appendChild(item)

})

})
}

function cancelar(nome, data, horario){

if(!confirm("Cancelar agendamento?")) return

fetch(`${API}/cancelar`,{
method:"POST",
headers:{ "Content-Type":"application/json" },
body: JSON.stringify({ nome, data, horario })
})
.then(() => {
alert("Cancelado!")
carregarAgenda()
})
}

window.onload = carregarAgenda