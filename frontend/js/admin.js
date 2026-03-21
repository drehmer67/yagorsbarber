const API = window.location.origin

function carregarAgenda(){

const dataFiltro = document.getElementById("filtroData").value
const barbeiroFiltro = document.getElementById("filtroBarbeiro").value

fetch(`${API}/agendamentos`)
.then(res => res.json())
.then(dados => {

const lista = document.getElementById("lista")
lista.innerHTML = ""

let total = 0

dados.forEach(a => {

if(dataFiltro && a.data != dataFiltro) return
if(barbeiroFiltro && a.barbeiro != barbeiroFiltro) return

total += Number(a.valor || 0)

const item = document.createElement("li")

item.innerHTML = `
<strong>${a.data} - ${a.horario}</strong><br>
👤 ${a.nome}<br>
💈 ${a.barbeiro}<br>
💈 Serviço: ${a.servico} <br>
💰 R$ ${a.valor}
<br><br>
<button onclick="cancelar('${a.nome}','${a.data}','${a.horario}')">❌ Cancelar</button>
`

lista.appendChild(item)

})

/* TOTAL */
const totalDiv = document.createElement("h2")
totalDiv.innerText = "💰 Total: R$ " + total

lista.appendChild(totalDiv)

})
.catch(error => {
console.log("Erro ao carregar agenda:", error)
})

}


function cancelar(nome, data, horario){

if(!confirm("Tem certeza que deseja cancelar?")) return

fetch(`${API}/cancelar`,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({nome, data, horario})
})
.then(() => {
alert("Agendamento cancelado")
carregarAgenda()
})

}


/* CARREGA AUTOMÁTICO */
carregarAgenda()