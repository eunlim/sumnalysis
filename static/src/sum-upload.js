import { createApp, ref, onMounted } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'

createApp({
    setup() {
        const text = ref('')
        const file = ref(null)
        const previewUrl = ref('')
        const isLoading = ref(false)

        onMounted(() => {
            // 연결
            const textarea = document.getElementById('textInput')
            const dropArea = document.getElementById('dropArea')
            const input = document.getElementById('imageInput')
            const preview = document.getElementById('preview')
            const loadingEl = document.getElementById('loading')

            textarea.addEventListener('input', () => text.value = textarea.value)

            dropArea.addEventListener('click', () => input.click())
            input.addEventListener('change', (e) => {
                const f = e.target.files[0]
                if (!f) return
                file.value = f
                previewUrl.value = URL.createObjectURL(f)
                preview.src = previewUrl.value
                ocrImage(f)
            })

            dropArea.addEventListener('dragover', e => e.preventDefault())
            dropArea.addEventListener('drop', e => {
                e.preventDefault()
                const f = e.dataTransfer.files[0]
                if (!f) return
                file.value = f
                previewUrl.value = URL.createObjectURL(f)
                preview.src = previewUrl.value
                ocrImage(f)
            })

            function ocrImage(f) {
                Tesseract.recognize(
                    f,
                    'kor', // 한국어 언어 설정
                    {
                        logger: m => console.log(m) // 진행률 로그
                    }
                ).then(({ data: { text: result } }) => {
                    text.value = result
                })
            }


            // async function ocrImage(f) {
            //     const form = new FormData()
            //     form.append('image', f)
            //     loadingEl.style.display = 'block'
            //     try {
            //
            //         const res = await axios.post('/api/ocr', form)
            //         text.value = res.data.text
            //         textarea.value = res.data.text
            //     } catch {
            //         alert('OCR 실패')
            //     } finally {
            //         loadingEl.style.display = 'none'
            //     }
            // }

            document.querySelector('[@click=\"submit\"]').addEventListener('click', async () => {
                if (!text.value.trim() && !file.value) {
                    alert('내용을 입력하거나 이미지를 업로드하세요.')
                    return
                }

                const form = new FormData()
                if (text.value) form.append('text', text.value)
                if (file.value) form.append('image', file.value)

                loadingEl.style.display = 'block'
                try {
                    const res = await axios.post('/api/summ/upload', form)
                    location.href = `/summ/result/${res.data.result_id}`
                } catch {
                    alert('업로드 실패')
                } finally {
                    loadingEl.style.display = 'none'
                }
            })
        })

        return {}
    }
}).mount('#summ-upload')