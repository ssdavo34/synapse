import streamlit as st
import chromadb

st.title("📚 SynapseSimple - 문서 조회")

# ChromaDB 클라이언트
chroma_client = chromadb.PersistentClient(path="data/vector_db")

# 세션 ID 입력
session_id = st.text_input("🔑 세션 ID 입력", placeholder="382d04a2-f8ce-4bcb-93cc-8f106afd9832")

if st.button("🔍 조회"):
    if session_id:
        try:
            # 컬렉션 조회
            collection_name = f"session_{session_id}"
            collection = chroma_client.get_collection(name=collection_name)

            # 데이터 가져오기
            results = collection.get(
                include=["documents", "metadatas"]
            )

            # 결과 표시
            st.success(f"✅ 세션 발견: {collection_name}")

            # 메타데이터
            metadata = collection.metadata
            if metadata:
                st.info(f"📁 파일명: {metadata.get('filename', 'N/A')}")

            # 청크 개수
            chunks_count = len(results['documents'])
            st.info(f"📊 청크 개수: {chunks_count}")

            # 각 청크 표시
            st.subheader("📄 문서 내용")
            for i, doc in enumerate(results['documents']):
                with st.expander(f"Chunk {i+1}"):
                    st.write(doc)

        except Exception as e:
            st.error(f"❌ 에러: {str(e)}")
    else:
        st.warning("⚠️ 세션 ID를 입력하세요")
