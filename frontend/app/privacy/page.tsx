"use client";

import { motion } from "framer-motion";
import { Shield, ArrowLeft, Mail } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function PrivacyPage() {
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
              <Shield className="h-6 w-6 text-blue-400" />
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Privacy Policy
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
            <h1 className="text-4xl font-bold text-white mb-4">Privacy Policy</h1>
            <p className="text-gray-400">Last updated: July 29, 2025</p>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-8 space-y-8">
            <div>
              <p className="text-gray-300 leading-relaxed">
                This Privacy Policy explains how AEON Investment Technologies ("we," "us," or "our") collects, uses, and protects your information when you use ATOM (the "Service") at https://aeoninvestmentstechnologies.com.
              </p>
            </div>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Information We Collect</h2>
              <ul className="text-gray-300 space-y-2 list-disc list-inside">
                <li><strong>Account Information:</strong> Basic data you provide (e.g., email, authentication info).</li>
                <li><strong>Usage Data:</strong> Analytics data, device/browser info, and log files.</li>
                <li><strong>Cookies:</strong> Used to operate and improve your experience.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">How We Use Your Information</h2>
              <ul className="text-gray-300 space-y-2 list-disc list-inside">
                <li>To provide, maintain, and secure the Service.</li>
                <li>For customer support and service improvement.</li>
                <li>To comply with legal obligations.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">How We Share Information</h2>
              <ul className="text-gray-300 space-y-2 list-disc list-inside">
                <li>We do <strong>not</strong> sell your information.</li>
                <li>We only share information with service providers and as required by law.</li>
                <li>We may share anonymized or aggregated data for analytics.</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Data Security</h2>
              <p className="text-gray-300 leading-relaxed">
                We use industry-standard safeguards, but cannot guarantee absolute security. You are responsible for maintaining the security of your own account credentials.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Your Rights</h2>
              <p className="text-gray-300 leading-relaxed">
                You may access, update, or request deletion of your information by contacting us at support@aeoninvestmentstechnologies.com.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Third Party Links</h2>
              <p className="text-gray-300 leading-relaxed">
                Our Service may contain links to third party sites. We are not responsible for the privacy practices or content of those sites.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Children's Privacy</h2>
              <p className="text-gray-300 leading-relaxed">
                ATOM is not intended for users under 18. We do not knowingly collect data from children.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Changes to This Policy</h2>
              <p className="text-gray-300 leading-relaxed">
                We may update this Privacy Policy at any time. Updates will be posted at this URL.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white mb-4">Contact</h2>
              <div className="flex items-center space-x-2 text-gray-300">
                <Mail className="h-5 w-5 text-blue-400" />
                <span>Questions? Email </span>
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
            <Link href="/terms">
              <Button variant="ghost" className="text-gray-400 hover:text-white">
                View Terms of Service
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
