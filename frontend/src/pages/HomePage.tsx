import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="min-h-screen bg-[#212121] flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center space-x-2">
          <div className="w-9 h-9 bg-[#10a37f] rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364 0 4.5 4.5 0 006.364 0 4.5 4.5 0 00-6.364 0zM15 6.364a4.5 4.5 0 000 6.364 0 4.5 4.5 0 006.364 0 4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <span className="text-white font-semibold text-lg">Clinical CDS</span>
        </div>
        <div className="flex items-center space-x-4">
          <Link to="/login" className="text-white text-sm hover:text-gray-300">
            Log in
          </Link>
          <Link 
            to="/register" 
            className="px-4 py-2 bg-[#10a37f] text-white text-sm rounded-lg hover:bg-[#0d8a6e]"
          >
            Sign up
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="max-w-3xl w-full text-center">
          {/* Simple Logo */}
          <div className="mb-8">
            <div className="w-16 h-16 bg-[#10a37f] rounded-2xl mx-auto flex items-center justify-center mb-6">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h1 className="text-5xl font-semibold text-white mb-4">
              Clinical Decision Support
            </h1>
            <p className="text-gray-400 text-lg">
              AI-powered medical information and symptom assessment
            </p>
          </div>

          {/* Simple Chat Input Preview */}
          <div className="bg-[#2f2f2f] rounded-xl p-4 mb-8 max-w-2xl mx-auto">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-[#19c37d] rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-gray-300 text-sm text-left flex-1">
                Describe your symptoms and get AI-powered medical information...
              </p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
            <Link
              to="/register"
              className="w-full sm:w-auto px-6 py-3 bg-[#10a37f] text-white text-base font-medium rounded-lg hover:bg-[#0d8a6e]"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-6 py-3 bg-[#212121] text-white text-base font-medium rounded-lg border border-gray-600 hover:bg-[#2f2f2f]"
            >
              Log in
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-4 py-6 text-center">
        <p className="text-gray-500 text-xs mb-2">
          This system provides decision-support information only and is not a substitute for professional medical advice.
        </p>
        <p className="text-gray-600 text-xs">
          © 2024 Clinical Decision Support System
        </p>
      </footer>
    </div>
  );
}