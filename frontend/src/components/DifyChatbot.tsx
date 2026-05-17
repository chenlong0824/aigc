import { useEffect } from 'react'

interface DifyChatbotProps {
  token: string
  baseUrl: string
}

export default function DifyChatbot({ token, baseUrl }: DifyChatbotProps) {
  useEffect(() => {
    if (!token || !baseUrl) {
      console.warn('DifyChatbot: token or baseUrl is missing')
      return
    }

    console.log('DifyChatbot: Loading for token:', token)

    const scriptId = `dify-script-${token}`
    const configId = `dify-config-${token}`

    const removeDifyElements = () => {
      const elements = document.querySelectorAll('[class*="dify"], [id*="dify"], [data-dify-chatbot]')
      elements.forEach(el => el.remove())
      
      const iframes = document.querySelectorAll('iframe[src*="dify"]')
      iframes.forEach(el => el.remove())
    }

    removeDifyElements()

    const configScript = document.createElement('script')
    configScript.id = configId
    configScript.innerHTML = `
      window.difyChatbotConfig = {
        token: '${token}',
        baseUrl: '${baseUrl}',
        inputs: {},
        systemVariables: {},
        userVariables: {},
        dynamicScript: true,
      };
      console.log('Dify config loaded:', window.difyChatbotConfig);
    `
    document.body.appendChild(configScript)

    const script = document.createElement('script')
    script.id = scriptId
    script.src = `${baseUrl}/embed.js`
    script.defer = true
    script.onload = () => console.log('DifyChatbot: Script loaded successfully')
    script.onerror = (error) => console.error('DifyChatbot: Script load failed', error)
    document.body.appendChild(script)

    return () => {
      const scriptToRemove = document.getElementById(scriptId)
      const configToRemove = document.getElementById(configId)
      if (scriptToRemove) scriptToRemove.remove()
      if (configToRemove) configToRemove.remove()
      
      removeDifyElements()
      
      const win = window as unknown as Record<string, unknown>
      if (win.difyChatbotConfig) {
        delete win.difyChatbotConfig
      }
    }
  }, [token, baseUrl])

  return null
}
