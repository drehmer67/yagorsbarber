const API = window.location.origin

function carregarAgenda(){

const dataFiltro = document.getElementById("filtroData").value
const barbeiroFiltro = document.getElementById("filtroBarbeiro").value
const valor = document.getElementById("valor").value

fetch(`${API}/agendamentos`)
.then(res => res.json())
.then(dados => {

const lista = document.getElementById("lista")
lista.innerHTML = ""

dados.forEach(a => {

if(dataFiltro && a.data != dataFiltro) return
if(barbeiroFiltro && a.barbeiro != barbeiroFiltro) return

const item = document.createElement("li")

item.innerHTML = `
${a.data} - ${a.horario} |
${a.nome} |
Barbeiro: ${a.barbeiro}
<button onclick="cancelar('${a.nome}','${a.data}','${a.horario}')">❌</button>
`

lista.appendChild(item)

})

})
.catch(error => {
console.log("Erro ao carregar agenda:", error)
})

}

function cancelar(nome, data, horario){

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

carregarAgenda()