const API = window.location.origin

if(localStorage.getItem("logado") !== "sim"){
window.location.href = "login.html"
}

function carregarAgenda(){

fetch(`${API}/agendamentos`)

.then(res => res.json())

.then(dados => {

const dataFiltro = document.getElementById("filtroData").value
const barbeiroFiltro = document.getElementById("filtroBarbeiro").value

const lista = document.getElementById("lista")

lista.innerHTML = ""

dados.forEach(a => {

if(dataFiltro && a.data != dataFiltro) return
if(barbeiroFiltro && a.barbeiro != barbeiroFiltro) return

const item = document.createElement("li")

item.innerHTML =
a.data + " - " + a.horario +
" | " + a.nome +
" | Barbeiro: " + a.barbeiro +
` <button onclick="cancelar('${a.nome}','${a.data}','${a.horario}')">Cancelar</button>`

lista.appendChild(item)

})

})

}

function cancelar(nome,data,horario){

fetch(`${API}/cancelar`,{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
nome:nome,
data:data,
horario:horario
})

})

.then(res => res.json())

.then(()=>{

alert("Agendamento cancelado")

carregarAgenda()

})

}

carregarAgenda()