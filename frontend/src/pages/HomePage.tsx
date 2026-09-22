import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="min-h-screen bg-[#212121] flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center space-x-2">
          <div className="w-9 h-9 bg-[#10a37f] rounded-xl flex items-center justify-center hover:bg-[#0d8a6e] transition-colors cursor-pointer">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364 0 4.5 4.5 0 006.364 0 4.5 4.5 0 00-6.364 0zM15 6.364a4.5 4.5 0 000 6.364 0 4.5 4.5 0 006.364 0 4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <span className="text-white font-semibold text-lg">Clinical CDS</span>
        </div>
        <div className="flex items-center space-x-4">
          <Link to="/login" className="text-white text-sm hover:text-gray-300 transition-colors">
            Log in
          </Link>
          <Link 
            to="/register" 
            className="px-4 py-2 bg-[#10a37f] text-white text-sm rounded-lg hover:bg-[#0d8a6e] transition-colors"
          >
            Sign up
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="max-w-4xl w-full text-center">
          {/* Logo */}
          <div className="mb-10">
            <div className="w-20 h-20 bg-gradient-to-br from-[#10a37f] to-[#0d8a6e] rounded-2xl mx-auto flex items-center justify-center mb-6 shadow-lg shadow-[#10a37f]/20">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h1 className="text-5xl md:text-6xl font-semibold text-white mb-4 tracking-tight">
              Clinical Decision Support
            </h1>
            <p className="text-gray-400 text-xl max-w-2xl mx-auto leading-relaxed">
              AI-powered medical information and symptom assessment to help you make informed healthcare decisions
            </p>
          </div>

          {/* Chat Preview */}
          <div className="bg-[#2f2f2f] rounded-2xl p-8 mb-10 max-w-3xl mx-auto shadow-2xl border border-gray-700">
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-gradient-to-br from-[#19c37d] to-[#15803d] rounded-full flex-shrink-0 flex items-center justify-center shadow-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-gray-100 text-base leading-relaxed">
                    Hello! I'm your clinical decision support assistant. I can help you understand your symptoms, provide medical information from approved sources like WHO and Rwanda Ministry of Health, and suggest when to seek professional care.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex-shrink-0 flex items-center justify-center shadow-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h6" />
                  </svg>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-gray-100 text-base leading-relaxed">
                    I have a headache and fever for two days. What should I do?
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-gradient-to-br from-[#19c37d] to-[#15803d] rounded-full flex-shrink-0 flex items-center justify-center shadow-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="flex-1 text-left">
                  <p className="text-gray-100 text-base leading-relaxed">
                    Based on your symptoms, I've identified headache and fever. These could indicate a viral infection. I recommend seeking medical attention if symptoms persist beyond 3 days or if fever exceeds 103°F. Would you like me to ask some follow-up questions to better understand your condition?
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4 mb-12">
            <Link
              to="/register"
              className="w-full sm:w-auto px-8 py-4 bg-[#10a37f] text-white text-base font-medium rounded-xl hover:bg-[#0d8a6e] transition-all hover:shadow-lg hover:shadow-[#10a37f]/20"
            >
              Get Started
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-4 bg-[#212121] text-white text-base font-medium rounded-xl border border-gray-600 hover:bg-[#2f2f2f] transition-all"
            >
              Log in
            </Link>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center group">
              <div className="w-16 h-16 bg-[#2f2f2f] rounded-2xl mx-auto mb-4 flex items-center justify-center group-hover:bg-[#3a3a3a] transition-colors">
                <svg className="w-8 h-8 text-[#10a37f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-white font-semibold text-lg mb-2">Symptom Analysis</h3>
              <p className="text-gray-400 text-sm leading-relaxed">AI-powered assessment of your symptoms with follow-up questions</p>
            </div>
            <div className="text-center group">
              <div className="w-16 h-16 bg-[#2f2f2f] rounded-2xl mx-auto mb-4 flex items-center justify-center group-hover:bg-[#3a3a3a] transition-colors">
                <svg className="w-8 h-8 text-[#10a37f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5-1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C13.832 18.477 12.246 18 10.5 18c-1.747 0-3.332-.477-4.5-1.253" />
                </svg>
              </div>
              <h3 className="text-white font-semibold text-lg mb-2">Medical Knowledge</h3>
              <p className="text-gray-400 text-sm leading-relaxed">Information from WHO, Rwanda MOH, and approved sources</p>
            </div>
            <div className="text-center group">
              <div className="w-16 h-16 bg-[#2f2f2f] rounded-2xl mx-auto mb-4 flex items-center justify-center group-hover:bg-[#3a3a3a] transition-colors">
                <svg className="w-8 h-8 text-[#10a37f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016M4.307 10.526c-.418 0-.526-.02-.526-.352V9.437c0-.332.108-.352.526-.352h.096c.406 0 .526.02.526.352v.122c0 .332-.12.352-.526.352H5.474c-.406 0-.526-.02-.526-.352v-.122c0-.332.12-.352.526-.352h.353c.406 0 .526.02.526.352v.122c0 .332-.12.352-.526-.352H5.18c-.406 0-.526-.02-.526-.352v-.122c0-.332.12-.352-.526-.352H6.54c.406 0 .526.02.526.352v.122c0 .332-.12.352-.526.352H9.35" />
                </svg>
              </div>
              <h3 className="text-white font-semibold text-lg mb-2">Safety First</h3>
              <p className="text-gray-400 text-sm leading-relaxed">Always consult qualified healthcare professionals</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-4 py-8 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="bg-[#2f2f2f] rounded-xl p-6 mb-4 border border-gray-700">
            <p className="text-gray-400 text-sm leading-relaxed mb-3">
              <span className="text-[#ffa500] font-medium">⚠️ Important:</span> This system provides decision-support information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns.
            </p>
            <p className="text-gray-500 text-xs">
              This system does not provide emergency medical services. For medical emergencies, call emergency services immediately.
            </p>
          </div>
          <p className="text-gray-600 text-xs">
            © 2024 Clinical Decision Support System • Built for Rwanda
          </p>
        </div>
      </footer>
    </div>
  );
}