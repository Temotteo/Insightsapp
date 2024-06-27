function carregarDados() {
      $.get('/saltar_org_id', function(data) {
          $('#modalTableBody').empty();
          data.forEach(function(item) {
              var linha = `<tr>
                              <td>${item.id}</td>
                              <td>${item.nome}</td>
                              <td>${item.Saldo}</td>
                              <td>
                                  <button class="btn btn-primary btn-sm" onclick="verDetalhes(${item.id})">
                                      <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span> Ver
                                  </button>
                              </td>
                          </tr>`;
              $('#modalTableBody').append(linha);
          });
          // Abre o modal após carregar os dados
          $('#Modal').modal('show');
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
