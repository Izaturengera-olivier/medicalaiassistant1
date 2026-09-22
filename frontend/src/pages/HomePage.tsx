import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="min-h-screen bg-[#212121] flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-[#10a37f] rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364 0 4.5 4.5 0 006.364 0 4.5 4.5 0 00-6.364 0 4.5 4.5 0 00-6.364 0zM15 6.364a4.5 4.5 0 000 6.364 0 4.5 4.5 0 006.364 0 4.5 4.5 0 00-6.364 0 4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <span className="text-white font-semibold">Clinical CDS</span>
        </div>
        <div className="flex items-center space-x-3">
          <Link to="/login" className="text-white text-sm hover:text-gray-300">
            Log in
          </Link>
          <Link to="/register" className="text-white text-sm hover:text-gray-300">
            Sign up
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="max-w-3xl w-full text-center">
          {/* Logo */}
          <div className="mb-8">
            <div className="w-16 h-16 bg-[#10a37f] rounded-full mx-auto flex items-center justify-center mb-4">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h1 className="text-4xl md:text-5xl font-semibold text-white mb-4">
              Clinical Decision Support
            </h1>
            <p className="text-gray-400 text-lg">
              AI-powered medical information and symptom assessment
            </p>
          </div>

          {/* Chat Preview */}
          <div className="bg-[#2f2f2f] rounded-xl p-6 mb-8 max-w-2xl mx-auto">
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#19c37d] rounded-full flex-shrink-0 flex items-center justify-center">
                  <span className="text-white text-xs font-semibold">AI</span>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-gray-200 text-sm">
                    Hello! I'm your clinical decision support assistant. I can help you understand your symptoms, provide medical information from approved sources, and suggest when to seek professional care.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gray-600 rounded-full flex-shrink-0 flex items-center justify-center">
                  <span className="text-white text-xs font-semibold">You</span>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-gray-200 text-sm">
                    I have a headache and fever for two days. What should I do?
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-[#19c37d] rounded-full flex-shrink-0 flex items-center justify-center">
                  <span className="text-white text-xs font-semibold">AI</span>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-gray-200 text-sm">
                    Based on your symptoms, I've identified headache and fever. These could indicate a viral infection. I recommend seeking medical attention if symptoms persist beyond 3 days or if fever exceeds 103°F. Would you like me to ask some follow-up questions?
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
            <Link
              to="/register"
              className="w-full sm:w-auto px-6 py-3 bg-[#10a37f] text-white rounded-lg hover:bg-[#0d8a6e] transition-colors"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-6 py-3 bg-[#212121] text-white border border-gray-600 rounded-lg hover:bg-[#2f2f2f] transition-colors"
            >
              Log in
            </Link>
          </div>

          {/* Features */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="w-12 h-12 bg-[#2f2f2f] rounded-lg mx-auto mb-3 flex items-center justify-center">
                <svg className="w-6 h-6 text-[#10a37f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-white font-medium mb-2">Symptom Analysis</h3>
              <p className="text-gray-400 text-sm">AI-powered assessment of your symptoms</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-[#2f2f2f] rounded-lg mx-auto mb-3 flex items-center justify-center">
                <svg className="w-6 h-6 text-[#10a37f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5-1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C13.832 18.477 12.246 18 10.5 18c-1.747 0-3.332-.477-4.5-1.253" />
                </svg>
              </div>
              <h3 className="text-white font-medium mb-2">Medical Knowledge</h3>
              <p className="text-gray-400 text-sm">Information from approved medical sources</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-[#2f2f2f] rounded-lg mx-auto mb-3 flex items-center justify-center">
                <svg className="w-6 h-6 text-[#10a37f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016M4.307 10.526c-.418 0-.526-.02-.526-.352V9.437c0-.332.108-.352.526-.352h.096c.406 0 .526.02.526.352v.122c0 .332-.12.352-.526.352H5.474c-.406 0-.526-.02-.526-.352v-.122c0-.332.12-.352.526-.352h.353c.406 0 .526.02.526.352v.122c0 .332-.12.352-.526.352H5.18c-.406 0-.526-.02-.526-.352v-.122c0-.332.12-.352.526-.352H6.54c.406 0 .526.02.526.352v.122c0 .332-.12.352-.526.352H9.35" />
                </svg>
              </div>
              <h3 className="text-white font-medium mb-2">Safety First</h3>
              <p className="text-gray-400 text-sm">Always consult healthcare professionals</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-4 py-6 text-center text-gray-500 text-sm">
        <p className="mb-2">
          This system provides decision-support information only and is not a substitute for professional medical advice, diagnosis, or treatment.
        </p>
        <p>
          © 2024 Clinical Decision Support System
        </p>
      </footer>
    </div>
  );
}
