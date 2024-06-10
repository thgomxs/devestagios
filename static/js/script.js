tipoUsuario = document.querySelector("#data-login-checker")


if (tipoUsuario){
    tipoUsuario = tipoUsuario.getAttribute("data-login-checker")
} else{
    if (localStorage.getItem("candidato") && !window.location.pathname.includes("coordenador"))
        localStorage.removeItem("candidato")

    if (localStorage.getItem("coordenador") && window.location.pathname.includes("coordenador"))
        localStorage.removeItem("coordenador")
}


// MUDANÇA DOS FORMULÁRIOS DE LOGIN/CADASTRO
loginForm = document.querySelector('#login_form')
registerForm = document.querySelector('#register_form')
buttons = document.querySelectorAll('.change_form')

buttons.forEach((button)=>{
    button.onclick = ()=>{
    loginForm.classList.toggle('d-none')
    registerForm.classList.toggle('d-none')
}
})


// TRECHO DO TOAST DO LOGOUT
const logoutForm = document.querySelector('#logout_form')
const logoutToast = document.querySelector('#logout_toast')

if (logoutForm) {
  const toastBootstrap = bootstrap.Toast.getOrCreateInstance(logoutToast)
  logoutForm.addEventListener('click', () => {
      toastBootstrap.show()
      localStorage.removeItem(tipoUsuario)
      setTimeout(()=>{
          logoutForm.submit()
      },2100)
  })
}

// ATIVAR E DESATIVAR MODO ESCURO
document.addEventListener('DOMContentLoaded', (event) => {
    const htmlElement = document.documentElement;
    const switchElement = document.getElementById('darkModeSwitch');

    const currentTheme = localStorage.getItem('theme') || 'dark';
    htmlElement.setAttribute('data-bs-theme', currentTheme);
    switchElement.checked = currentTheme === 'dark';

    switchElement.addEventListener('change', function () {
        if (this.checked) {
            htmlElement.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });
});


// VALIDAÇÃO DE FORMULARIOS DO BOOTSTRAP
const forms = document.querySelectorAll('.needs-validation')

Array.from(forms).forEach(form => {
form.addEventListener('submit', event => {
  if (!form.checkValidity()) {
    event.preventDefault()
    event.stopPropagation()
  }

  form.classList.add('was-validated')
}, false)
})

if (tipoUsuario === "candidato"){

    const avaliacaoButton = document.querySelector('#avaliacaoButton')

    avaliacaoButton.addEventListener('click', event => {
        event.preventDefault()
        document.querySelector("#avaliacaoDiv").innerHTML = ""
        document.querySelector('#spinnerAvaliacao').style.display = 'block';
        document.querySelector('#backAvaliacaoButton').style.display = 'none';
        fetch("/candidato_avaliar")
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Erro ao obter informação');
                        }
                        return response.json();
                    })
                    .then(data => {
                        dados = JSON.parse(data)
                        // Atualiza o conteúdo da div com a informação recebida do backend
                        document.querySelector('#spinnerAvaliacao').style.display = 'none';
                        document.querySelector('#backAvaliacaoButton').style.display = 'block';
                        if (dados.erro){
                            document.querySelector("#avaliacaoDiv").innerHTML = ` <p style="text-align: justify" class="text-danger"><span class="fw-bold text-uppercase text-danger">Erro: </span>${dados.erro}</p>`;
                        }else {
                            document.querySelector("#avaliacaoDiv").innerHTML = `<p><span class="fw-bold text-uppercase">
                                            Nota da sua descrição (0-10):</span> ${dados.nota} </p>  
                                            <p style="text-align: justify"><span class="fw-bold text-uppercase">Comentário</span> ${dados.comentario}</p>`;
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                    });
    })

    const compatibilidadeButtons = document.querySelectorAll(".compatibilidadeButton")

    compatibilidadeButtons.forEach(button =>{
        button.addEventListener('click', event => {
            event.preventDefault()
            document.querySelector("#compatibilidadeDiv").innerHTML = ""
            document.querySelector('#spinnerCompatibilidade').style.display = 'block';
            document.querySelector('#backCompatibilidadeButton').style.display = 'none';
            const vaga_id = button.getAttribute('data-id')
            const url = "/candidato_compatibilidade/" + vaga_id
            fetch(url,{
                method: "POST",
                headers: { "Content-Type": "application/json",}}
            )
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Erro ao obter informação');
                            }
                            return response.json();
                        })
                        .then(data => {
                            dados = JSON.parse(data)
                            // Atualiza o conteúdo da div com a informação recebida do backend
                            document.querySelector('#spinnerCompatibilidade').style.display = 'none';
                            document.querySelector('#backCompatibilidadeButton').style.display = 'block';
                            if (dados.erro){
                                  document.querySelector("#compatibilidadeDiv").innerHTML = ` <p style="text-align: justify" class="text-danger"><span class="fw-bold text-uppercase">Erro: </span>${dados.erro}</p>`;
                            } else{
                                  document.querySelector("#compatibilidadeDiv").innerHTML = `<p><span class="fw-bold text-uppercase">Porcentagem: </span> Sua descrição é ${dados.porcentagem}% compativel com essa vaga</p> 
                                  <p style="text-align: justify"><span class="fw-bold text-uppercase">Comentário: </span>${dados.comentario}</p>`;

                            }
                                                  })
                        .catch(error => {
                            console.error('Erro:', error);
                        });

    })
    })
}

if (tipoUsuario === "coordenador"){
    const sugestaoButtons = document.querySelectorAll(".sugestaoButton")

    sugestaoButtons.forEach(button =>{
        button.addEventListener('click', event => {
            document.querySelector("#sugestaoDiv").innerHTML = ""
            document.querySelector('#spinnerSugestao').style.display = 'block';
            document.querySelector('#backSugestaoButton').style.display = 'none';
            document.querySelector('#formConfirmarCandidato').style.display = 'none';
            const vaga_id = button.getAttribute('data-id')
            document.querySelector('#backSugestaoButton').setAttribute("data-bs-target", `#ver_candidatos_${vaga_id}`)
            const url = "/coordenador_sugerir_candidato/" + vaga_id
            fetch(url,{
                method: "POST",
                headers: { "Content-Type": "application/json",}}
            )
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Erro ao obter informação');
                            }
                            return response.json();
                        })
                        .then(data => {
                            candidatoSelecionado = JSON.parse(data)
                            // Atualiza o conteúdo da div com a informação recebida do backend
                            document.querySelector('#spinnerSugestao').style.display = 'none';
                            document.querySelector('#backSugestaoButton').style.display = 'block';
                            if (candidatoSelecionado.erro){
                               document.querySelector("#sugestaoDiv").innerHTML = ` <p style="text-align: justify" class="text-danger"><span class="fw-bold text-uppercase">Erro: </span>${candidatoSelecionado.erro}</p>`;
                            } else{
                                document.querySelector('#formConfirmarCandidato').style.display = 'block';
                                document.querySelector("#sugestaoDiv").innerHTML = `                                        
                                        <div class="card mb-5 shadow ">
                                          <div class="card-header p-3 d-flex justify-content-start align-items-center">
                                              <p class="fs-5 fw-bold p-0 m-0 text-uppercase ">${candidatoSelecionado.nome}</p>
                                          </div>
                                          <div class="card-body p-3 small">
                                            <p class="card-text text-uppercase mb-1"><span class="fw-bold me-1">Email:</span>${candidatoSelecionado.email}</p>
                                            <p class="card-text text-uppercase mb-1"><span class="fw-bold me-1">Data de nascimento:</span>${candidatoSelecionado.nascimentoFormatado}</p>
                                          </div>
                                        </div>
                                        <p style="text-align: justify"><span class="fw-bold text-uppercase">Comentário: </span>${candidatoSelecionado.comentario}</p>`;
                            }

                            document.querySelector("#formConfirmarCandidato").setAttribute("action", `/coordenador_confirmar_candidato/${candidatoSelecionado.vaga_id}/${candidatoSelecionado.id}`)
                        })
                        .catch(error => {
                            console.error('Erro:', error);
                        });

    })
    })
}

document.addEventListener('DOMContentLoaded', (event) => {
    const loginToast = document.querySelector('#login_toast')
    const toastLoginBootstrap = bootstrap.Toast.getOrCreateInstance(loginToast);

    if (tipoUsuario === 'candidato' && !localStorage.getItem("candidato")) {
        localStorage.setItem('candidato', "True");
        toastLoginBootstrap.show();
    }

    if (tipoUsuario === 'coordenador' && !localStorage.getItem("coordenador")) {
        localStorage.setItem('coordenador', "True");
        toastLoginBootstrap.show();
    }
});