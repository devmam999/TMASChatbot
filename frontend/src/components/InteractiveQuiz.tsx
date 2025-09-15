import React, { useState } from 'react';

export interface QuizQuestion {
  question: string;
  options: { [key: string]: string };
  correctAnswer: string;
  explanation: string;
  hint: string;
}

interface InteractiveQuizProps {
  questions: QuizQuestion[];
  onClose: () => void;
  onComplete?: (summary: { correct: number; total: number; percentage: number }) => void;
}

const InteractiveQuiz: React.FC<InteractiveQuizProps> = ({ questions, onClose, onComplete }) => {
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: string }>({});
  const [submitted, setSubmitted] = useState<{ [key: number]: boolean }>({});
  const [showHints, setShowHints] = useState<{ [key: number]: boolean }>({});
  const [showExplanations, setShowExplanations] = useState<{ [key: number]: boolean }>({});

  const handleAnswerSelect = (questionIndex: number, answer: string) => {
    if (submitted[questionIndex]) return; // Can't change after submission
    
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }));
  };

  const handleSubmit = (questionIndex: number) => {
    setSubmitted(prev => ({
      ...prev,
      [questionIndex]: true
    }));
  };

  const toggleHint = (questionIndex: number) => {
    setShowHints(prev => ({
      ...prev,
      [questionIndex]: !prev[questionIndex]
    }));
  };

  const toggleExplanation = (questionIndex: number) => {
    setShowExplanations(prev => ({
      ...prev,
      [questionIndex]: !prev[questionIndex]
    }));
  };

  const getScore = () => {
    let correct = 0;
    let total = 0;
    
    Object.keys(submitted).forEach(questionIndexStr => {
      const questionIndex = parseInt(questionIndexStr);
      if (submitted[questionIndex]) {
        total++;
        if (selectedAnswers[questionIndex] === questions[questionIndex].correctAnswer) {
          correct++;
        }
      }
    });
    
    return { correct, total };
  };

  const { correct, total } = getScore();
  const percentage = total > 0 ? Math.round((correct / total) * 100) : 0;

  // When all questions submitted, call onComplete once
  const allSubmitted = total === questions.length && questions.length > 0;
  const hasCalledRef = React.useRef(false);
  React.useEffect(() => {
    if (allSubmitted && !hasCalledRef.current && onComplete) {
      hasCalledRef.current = true;
      onComplete({ correct, total, percentage });
    }
  }, [allSubmitted, onComplete, correct, total, percentage]);

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-4">
      {/* Quiz Header with Score */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <h3 className="text-xl font-semibold text-blue-900">🧠 Interactive Quiz</h3>
          <span className="text-sm text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
            {questions.length} Questions
          </span>
        </div>
        <div className="flex items-center space-x-3">
          {total > 0 && (
            <>
              <div className="text-sm text-blue-700">
                Score: <span className="font-semibold">{correct}/{total}</span>
              </div>
              <div className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full font-medium">
                {percentage}%
              </div>
            </>
          )}
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-sm px-3 py-1 rounded-lg border border-gray-300 hover:border-gray-400 transition-colors"
          >
            ✕ Close Quiz
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {questions.map((question, questionIndex) => {
          const isSubmitted = submitted[questionIndex];
          const selectedAnswer = selectedAnswers[questionIndex];
          const isCorrect = selectedAnswer === question.correctAnswer;
          const showHint = showHints[questionIndex];
          const showExplanation = showExplanations[questionIndex];

          return (
            <div key={questionIndex} className="bg-white rounded-lg p-4 border border-blue-100">
              {/* Question */}
              <div className="mb-4">
                <h4 className="text-lg font-medium text-gray-800 mb-2">
                  <span className="text-blue-600">Q{questionIndex + 1}:</span> {question.question}
                </h4>
              </div>

              {/* Multiple Choice Options */}
              <div className="space-y-2 mb-4">
                {Object.entries(question.options).map(([option, text]) => {
                  const isSelected = selectedAnswer === option;
                  const isCorrectOption = option === question.correctAnswer;
                  
                  let optionStyle = "border-2 border-gray-200 hover:border-blue-300 cursor-pointer";
                  let textStyle = "text-gray-700";
                  
                  if (isSubmitted) {
                    if (isCorrectOption) {
                      optionStyle = "border-2 border-green-500 bg-green-50";
                      textStyle = "text-green-800 font-medium";
                    } else if (isSelected && !isCorrect) {
                      optionStyle = "border-2 border-red-500 bg-red-50";
                      textStyle = "text-red-800 font-medium";
                    }
                  } else if (isSelected) {
                    optionStyle = "border-2 border-blue-500 bg-blue-50";
                    textStyle = "text-blue-800 font-medium";
                  }

                  return (
                    <div
                      key={option}
                      className={`p-3 rounded-lg transition-colors ${optionStyle}`}
                      onClick={() => handleAnswerSelect(questionIndex, option)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-sm font-medium ${
                          isSelected 
                            ? isSubmitted && isCorrect 
                              ? 'border-green-500 bg-green-500 text-white' 
                              : isSubmitted && !isCorrect 
                                ? 'border-red-500 bg-red-500 text-white'
                                : 'border-blue-500 bg-blue-500 text-white'
                            : 'border-gray-300 text-gray-400'
                        }`}>
                          {option}
                        </div>
                        <span className={textStyle}>{text}</span>
                        {isSubmitted && isCorrectOption && (
                          <span className="text-green-600 text-sm font-medium">✓ Correct</span>
                        )}
                        {isSubmitted && isSelected && !isCorrect && (
                          <span className="text-red-600 text-sm font-medium">✗ Incorrect</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-3 mb-4">
                {!isSubmitted ? (
                  <button
                    onClick={() => handleSubmit(questionIndex)}
                    disabled={!selectedAnswer}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      selectedAnswer
                        ? 'bg-blue-500 text-white hover:bg-blue-600'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    Submit Answer
                  </button>
                ) : (
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                      isCorrect 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {isCorrect ? 'Correct!' : 'Incorrect'}
                    </span>
                  </div>
                )}

                <button
                  onClick={() => toggleHint(questionIndex)}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  {showHint ? 'Hide Hint' : 'Show Hint'}
                </button>

                {isSubmitted && (
                  <button
                    onClick={() => toggleExplanation(questionIndex)}
                    className="text-green-600 hover:text-green-800 text-sm font-medium"
                  >
                    {showExplanation ? 'Hide Explanation' : 'Show Explanation'}
                  </button>
                )}
              </div>

              {/* Hint */}
              {showHint && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                  <div className="flex items-start space-x-2">
                    <span className="text-yellow-600 text-lg">💡</span>
                    <span className="text-yellow-800 text-sm">{question.hint}</span>
                  </div>
                </div>
              )}

              {/* Explanation */}
              {showExplanation && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-start space-x-2">
                    <span className="text-green-600 text-lg">✅</span>
                    <span className="text-green-800 text-sm">{question.explanation}</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Final Score Display */}
  {total > 0 && total === questions.length && (
        <div className="mt-6 p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-white text-center">
          <h4 className="text-xl font-semibold mb-2">Quiz Complete! 🎉</h4>
          <p className="text-lg">
            You scored <span className="font-bold">{correct}/{total}</span> ({percentage}%)
          </p>
          <p className="text-blue-100 text-sm mt-1">
            {percentage >= 80 ? 'Excellent work!' : 
             percentage >= 60 ? 'Good job!' : 
             percentage >= 40 ? 'Keep practicing!' : 'Review the material and try again!'}
          </p>
        </div>
      )}
    </div>
  );
};

export default InteractiveQuiz; 