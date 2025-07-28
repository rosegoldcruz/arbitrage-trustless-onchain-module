'use client'

import { useEffect, useState } from 'react'
import { Web3Auth } from '@web3auth/modal'
import { CHAIN_NAMESPACES } from '@web3auth/base'
import { OpenloginAdapter } from '@web3auth/openlogin-adapter'
import { EthereumPrivateKeyProvider } from '@web3auth/ethereum-provider'
import { useRouter } from 'next/navigation'

const clientId = process.env.NEXT_PUBLIC_WEB3AUTH_CLIENT_ID || ''

export default function LoginPage() {
  const [web3auth, setWeb3auth] = useState<Web3Auth | null>(null)
  const [userAddress, setUserAddress] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const init = async () => {
      const instance = new Web3Auth({
        clientId,
        chainConfig: {
          chainNamespace: CHAIN_NAMESPACES.EIP155,
          chainId: '0x14A33', // Base Sepolia
          rpcTarget: 'https://base-sepolia.g.alchemy.com/v2/ESBtk3UKjPt2rK2Yz0hnzUj0tIJGTe-d'
        },
        uiConfig: {
          appLogo: 'https://aeoninvestmentstechnologies.com/logo.png',
          theme: 'dark',
          loginMethodsOrder: ['google', 'email_passwordless', 'metamask']
        },
        web3AuthNetwork: 'testnet'
      })

      const openloginAdapter = new OpenloginAdapter({
        adapterSettings: {
          uxMode: 'popup',
          whiteLabel: {
            name: 'AEON',
            logoLight: 'https:
