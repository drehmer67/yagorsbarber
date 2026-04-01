const API = window.location.origin

function carregarAgenda(){

fetch(`${API}/agendamentos`)
.then(res => res.json())
.then(lista => {

const container = document.getElementById("lista")
container.innerHTML = ""

const hoje = new Date().toISOString().split("T")[0]

lista.forEach(a => {

const statusClass = a.status === "finalizado" ? "finalizado" : "pendente"

const item = document.createElement("div")
item.className = "card-agendamento " + statusClass

// 📲 mensagem whatsapp
const mensagem = `Olá ${a.nome}! 💈

Lembrando do seu horário:

📅 ${a.data}
⏰ ${a.horario}

Barbearia Yagor's Barber`

const telefone = "55" + a.telefone || "5551999999999"
const urlWhats = `https://wa.me/${telefone}?text=${encodeURIComponent(mensagem)}`

item.innerHTML = `
<h3>${a.nome}</h3>

<p>💈 ${a.barbeiro}</p>
<p>📅 ${a.data}</p>
<p>⏰ ${a.horario}</p>
<p>💰 R$ ${a.valor}</p>
<p>📌 ${a.status || "pendente"}</p>

<div class="acoes-card">

<button onclick="window.open('${urlWhats}')">📲 Avisar</button>

<button onclick="finalizar('${a.nome}','${a.data}','${a.horario}')">
✅ Finalizar
</button>

<button onclick="cancelar('${a.nome}','${a.data}','${a.horario}')">
❌ Cancelar
</button>

</div>
`
mostrarProximo(lista)
container.appendChild(item)

})

})
}

function finalizar(nome, data, horario){

fetch(`${API}/finalizar`,{
method:"POST",
headers:{ "Content-Type":"application/json" },
body: JSON.stringify({ nome, data, horario })
})
.then(() => {
alert("Atendimento finalizado!")
carregarAgenda()
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

function mostrarProximo(lista){

const agora = new Date()

const futuros = lista.filter(a => {
  const dataHora = new Date(`${a.data}T${a.horario}`)
  return dataHora >= agora && a.status !== "finalizado"
})

if(futuros.length === 0){
  document.getElementById("proximo").innerText = "Sem próximos atendimentos"
  return
}

futuros.sort((a,b)=>{
  return new Date(`${a.data}T${a.horario}`) - new Date(`${b.data}T${b.horario}`)
})

const p = futuros[0]

document.getElementById("proximo").innerText =
`🔔 Próximo: ${p.nome} às ${p.horario}`
}