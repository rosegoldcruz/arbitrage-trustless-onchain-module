"use client";

import { motion } from "framer-motion";
import { FileText, ArrowLeft, Mail, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      {/* Header */}
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <FileText className="h-6 w-6 text-blue-400" />
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Terms of Service
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="prose prose-invert prose-lg max-w-none"
        >
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">Terms of Service</h1>
            <p className="text-gray-400">Last updated: July 29, 2025</p>
          </div>

          {/* Important Disclaimer */}
          <Alert className="mb-8 border-yellow-600 bg-yellow-900/20">
            <AlertTriangle className="h-4 w-4 text-yellow-400" />
            <AlertDescription className="text-yellow-200">
              <strong>Important:</strong> AEON Investment Technologies is not a registered broker, dealer, investment advisor, or financial planner. This platform is for informational purposes only.
            </AlertDescription>
          </Alert>

          <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-8 space-y-8">
            <div>
              <p className="text-gray-300 leading-relaxed">
                Welcome to ATOM, a service provided by AEON Investment Technologies. By accessing or using ATOM at https://aeoninvestmentstechnologies.com, you ("User") agree to these terms:
              </p>
            </div>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Use of Service</h2>
              <ul className="text-gray-300 space-y-2 list-disc list-inside">
                <li>You must be at least 18 years old.</li>
                <li>You agree not to use ATOM for illegal or unauthorized purposes.</li>
                <li>We may restrict or terminate your access at any time for any reason.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">No Financial Advice</h2>
              <div className="bg-red-900/20 border border-red-600 rounded-lg p-4 mb-4">
                <p className="text-red-200 leading-relaxed">
                  All content and functionality on ATOM are for informational purposes only and do not constitute financial, investment, legal, or other professional advice.
                </p>
              </div>
              <p className="text-gray-300 leading-relaxed">
                <strong>AEON Investment Technologies is not a registered broker, dealer, investment advisor, or financial planner.</strong> No information provided by the Service should be construed as a recommendation or solicitation for any investment or financial strategy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">No Offer, No Solicitation</h2>
              <p className="text-gray-300 leading-relaxed">
                Nothing on this site constitutes an offer or solicitation to buy or sell any financial instrument or to participate in any particular trading strategy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Risk Disclosure</h2>
              <div className="bg-orange-900/20 border border-orange-600 rounded-lg p-4">
                <p className="text-orange-200 leading-relaxed">
                  Digital assets and DeFi activities are inherently risky and may result in loss of principal. By using ATOM, you acknowledge and accept all risks associated with blockchain, smart contracts, and trading.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Intellectual Property</h2>
              <p className="text-gray-300 leading-relaxed">
                All logos, code, and content are owned by AEON Investment Technologies. No copying, redistribution, or reverse engineering is permitted.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Disclaimer of Warranties</h2>
              <p className="text-gray-300 leading-relaxed">
                ATOM is provided "as is" and "as available." We make <strong>no warranties or guarantees</strong> of any kind regarding accuracy, security, or uninterrupted service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Limitation of Liability</h2>
              <p className="text-gray-300 leading-relaxed">
                To the fullest extent allowed by law, AEON Investment Technologies and its affiliates disclaim all liability for any damages or losses arising from your use of the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Indemnity</h2>
              <p className="text-gray-300 leading-relaxed">
                You agree to indemnify and hold harmless AEON Investment Technologies from any claims, damages, or expenses resulting from your use of the Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Changes to Terms</h2>
              <p className="text-gray-300 leading-relaxed">
                We may update these Terms at any time. Continued use means you accept the new Terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Governing Law</h2>
              <p className="text-gray-300 leading-relaxed">
                These Terms are governed by the laws of the United States and the State of Delaware.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Contact</h2>
              <div className="flex items-center space-x-2 text-gray-300">
                <Mail className="h-5 w-5 text-blue-400" />
                <span>For legal or support inquiries, email </span>
                <a 
                  href="mailto:support@aeoninvestmentstechnologies.com" 
                  className="text-blue-400 hover:text-blue-300 transition-colors"
                >
                  support@aeoninvestmentstechnologies.com
                </a>
              </div>
            </section>
          </div>

          {/* Footer Navigation */}
          <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col sm:flex-row justify-between items-center">
            <Link href="/" className="mb-4 sm:mb-0">
              <Button variant="outline" className="border-gray-700 text-gray-300 hover:text-white">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
            </Link>
            <Link href="/privacy">
              <Button variant="ghost" className="text-gray-400 hover:text-white">
                View Privacy Policy
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
