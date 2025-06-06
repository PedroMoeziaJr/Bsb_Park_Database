# --- CONSULTA DE ENTRADAS POR DIA ---
st.subheader("Consultar entradas por data")

data_consulta = st.date_input("Selecione a data para consulta", value=datetime.now().date())
inicio_dia = datetime.combine(data_consulta, datetime.min.time()).isoformat()
fim_dia = datetime.combine(data_consulta, datetime.max.time()).isoformat()

try:
    consulta = supabase.table("entradas") \
        .select("id_entrada, tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada") \
        .gte("data_entrada", inicio_dia) \
        .lte("data_entrada", fim_dia) \
        .order("data_entrada", desc=True) \
        .execute()

    # Filtra somente os clientes da lista do SCS
    entradas_filtradas = [e for e in consulta.data if e["tipo_cliente"] in clientes_lista]

    if entradas_filtradas:
        st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')}")
        total_valor = 0
        entradas_a_excluir = []

        for entrada in entradas_filtradas:
            cliente = entrada["tipo_cliente"]
            valor = entrada["valor_entrada"]
            pagamento = entrada["forma_pagamento"]
            qtd = entrada["qtd_entradas"]
            entrada_id = entrada["id_entrada"]
            data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")

            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora}")
            with col2:
                if st.checkbox("Excluir", key=entrada_id):
                    entradas_a_excluir.append(entrada_id)

            total_valor += valor

        st.success(f"💰 Total do dia: R$ {total_valor:.2f}")

        if entradas_a_excluir:
            if st.button("Excluir selecionados"):
                try:
                    for id_excluir in entradas_a_excluir:
                        supabase.table("entradas").delete().eq("id_entrada", id_excluir).execute()
                    st.success("Entradas excluídas com sucesso.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir entradas: {e}")
    else:
        st.info("Nenhuma entrada encontrada para esta data.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")
