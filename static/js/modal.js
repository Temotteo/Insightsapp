function carregarDados() {
      $.get('/saltar_org_id', function(data) {
          $('#modalTableBody').empty();
          data.forEach(function(item) {
              var linha = `<tr>
                              <td>${item.id}</td>
                              <td>${item.nome}</td>
                              <td>${item.Saldo}</td>
                              <td>
                                  <button class="btn btn-primary btn-sm" onclick="verDetalhes('${item.id}')">
                                      <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> Ver
                                  </button>
                              </td>
                          </tr>`;
              $('#modalTableBody').append(linha);
          });
          // Abre o modal após carregar os dados
          $('#ModalOrg').modal('show');
      });
  }

  function smsGrupo() {
   
        $('#modalBodySms').empty();
            var linha = `
                      <div class="form-group">
                        <label for="mensagem">Mensage:</label>
                         <textarea type="text" class="form-control" id="mensagem" row="5" name="mensagem"  required ></textarea>
                         </div><div class="form-group">
                             <label for="country" class="form-label">Grupo</label>
                              <select class="form-control" id="country"  name ="grupo" >
                                <option value="">selecione...</option>
                            `;
                            $.get('/selecionar_group', function(data) {
                                data.forEach(function(item) {
                                    linha += `<option value="${item.id}">${item.nome}</option>`;
                                });
                        
                                // Fecha a tag select e adiciona o botão de enviar
                                linha += `</select>
                                          </div>
                                          <button class="btn btn-primary btn-sm" onclick="enviar_sms_grupo()">
                                              <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> enviar
                                          </button>`;
            $('#modalBodySms').append(linha);
        
        // Abre o modal após carregar os dados
        $('#ModalSmsGroup').modal('show');
    });
}


  function verDetalhes(id) {
      fetch(`/get_org/${id}`, {
              method: 'GET'
          })
          .then(response => {
              if (response.redirected) {
                  window.location.href = response.url;
              }
          })
          .catch(error => {
              console.error('Erro ao enviar dados:', error);
          });
  }

  function enviar_sms_grupo() {
    var grupoId = $('#country').val();
    var smsData = {
        grupo: grupoId,
        // Adicione outros campos do formulário aqui, se necessário
        mensagem: $('#mensagem').val(), // Supondo que você tenha um campo de mensagem no formulário
           // Supondo que você tenha um campo de contato no formulário
    };

    fetch('/enviar_sms_grupo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(smsData)
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            console.log('Resposta do servidor:', data);
        })
        .catch(error => {
            console.error('Erro ao enviar dados:', error);
        });
}

function close() {
    // Aqui você pode adicionar a lógica para salvar os dados na tabela
    alert('chueguei')
};
