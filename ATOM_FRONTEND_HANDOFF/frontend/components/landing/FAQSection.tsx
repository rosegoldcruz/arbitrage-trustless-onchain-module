"use client";

import { motion } from "framer-motion";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export function FAQSection() {
  const faqs = [
    {
      question: "What is arbitrage and how does ATOM make it risk-free?",
      answer: "Arbitrage involves buying an asset on one exchange and selling it on another to profit from price differences. ATOM makes this risk-free by using flash loans - you borrow the capital, execute the trade, and repay the loan all in a single transaction. If the arbitrage isn't profitable, the entire transaction fails and you lose nothing."
    },
    {
      question: "Do I need any capital to start using ATOM?",
      answer: "No! That's the beauty of flash loans. You don't need any upfront capital. The flash loan provides the necessary funds for each arbitrage opportunity, and you only pay a small fee (typically 0.05-0.09%) on the borrowed amount. You keep all the profits after repaying the loan and fees."
    },
    {
      question: "How much can I expect to earn with ATOM?",
      answer: "Earnings vary based on market conditions, gas fees, and the frequency of arbitrage opportunities. Our users typically see returns ranging from 5-20% APY, with some experiencing higher returns during volatile market periods. The AI agents work 24/7 to maximize opportunities."
    },
    {
      question: "What are the risks involved?",
      answer: "The main risks are gas fees (if a transaction fails, you still pay gas) and smart contract risks. However, our platform uses battle-tested protocols like AAVE for flash loans and has undergone extensive security audits. The arbitrage itself is risk-free due to the atomic nature of flash loan transactions."
    },
    {
      question: "Which blockchains and DEXs does ATOM support?",
      answer: "ATOM currently supports Ethereum, Base, Arbitrum, and Polygon networks. We integrate with major DEXs including Uniswap, Curve, SushiSwap, and others. We're constantly adding support for new chains and exchanges to maximize arbitrage opportunities."
    },
    {
      question: "How do the AI agents work?",
      answer: "Our AI agents (ATOM, ADOM, and MEV Sentinel) continuously monitor price feeds across multiple DEXs. They use advanced algorithms to detect profitable arbitrage opportunities, calculate optimal trade sizes, and execute transactions automatically. MEV Sentinel also protects against front-running attacks."
    },
    {
      question: "Can I customize the trading strategies?",
      answer: "Yes! Pro and Enterprise plans include access to our strategy builder where you can set custom parameters like minimum profit thresholds, preferred trading pairs, gas price limits, and risk tolerance levels. You can also pause or resume agents at any time."
    },
    {
      question: "What happens if the market moves against me during a trade?",
      answer: "This is impossible with flash loans! The entire arbitrage operation happens in a single atomic transaction. If any part of the trade would result in a loss, the entire transaction reverts and you're not charged anything except the failed transaction gas fee."
    },
    {
      question: "How do I get started?",
      answer: "Simply connect your wallet, choose a plan, and our AI agents will start working immediately. You can monitor all activities through our dashboard and withdraw profits at any time. We offer a 14-day free trial so you can test the platform risk-free."
    },
    {
      question: "Is ATOM audited and secure?",
      answer: "Yes, ATOM has been audited by leading blockchain security firms. We use established protocols like AAVE for flash loans and follow best practices for smart contract security. All code is open-source and regularly updated to address any potential vulnerabilities."
    }
  ];

  return (
    <section id="faq" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900/30">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-300">
            Everything you need to know about ATOM and DeFi arbitrage
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="bg-gray-900/50 border border-gray-700 rounded-lg px-6"
              >
                <AccordionTrigger className="text-left text-white hover:text-blue-400 transition-colors">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-gray-300 leading-relaxed">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </motion.div>
      </div>
    </section>
  );
}
