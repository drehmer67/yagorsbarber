const API = window.location.origin

function carregarAgenda(){

fetch(`${API}/agendamentos`)
.then(res => res.json())
.then(lista => {

const container = document.getElementById("lista")
container.innerHTML = ""

// 🔔 mostra próximo atendimento
mostrarProximo(lista)

lista.forEach(a => {

const statusClass = a.status === "finalizado" ? "finalizado" : "pendente"

const item = document.createElement("div")
item.className = "card-agendamento " + statusClass

// 📲 mensagem whatsapp (SEM BUG)
const mensagem = `Olá ${a.nome}! 💈

Lembrando do seu horário:

📅 ${a.data}
⏰ ${a.horario}

Barbearia Yagors Barber`

// 📞 telefone corrigido
const telefone = a.telefone ? "55" + a.telefone : "5551999999999"

// 🔗 link whatsapp
const urlWhats = `https://wa.me/${telefone}?text=${encodeURIComponent(mensagem)}`

item.innerHTML = `
<h3>${a.nome}</h3>

<p>💈 ${a.barbeiro}</p>
<p>📅 ${a.data}</p>
<p>⏰ ${a.horario}</p>
<p>💰 R$ ${a.valor}</p>
<p>📌 ${a.status || "pendente"}</p>

<div class="acoes-card">

<button onclick="window.open('${urlWhats}', '_blank')">📲 Avisar</button>

<button onclick="finalizar('${a.nome}','${a.data}','${a.horario}')">
✅ Finalizar
</button>

<button onclick="cancelar('${a.nome}','${a.data}','${a.horario}')">
❌ Cancelar
</button>

</div>
`

container.appendChild(item)

})

})
.catch(err => {
console.log("Erro ao carregar agenda:", err)
})

}

// ✅ FINALIZAR
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
.catch(err => {
console.log("Erro ao finalizar:", err)
})

}

// ❌ CANCELAR
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
.catch(err => {
console.log("Erro ao cancelar:", err)
})

}

// 🔔 PRÓXIMO ATENDIMENTO
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

// 🚀 INICIAR
window.onload = carregarAgenda