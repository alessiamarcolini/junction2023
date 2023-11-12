import { SystemMessageContainer } from './SystemMessageContainer'
import { RECOMMENDED_DEMO_MESSAGES } from '../constants'
import { DemoMessageContainer } from './DemoMessageContainer'

type Props = {
 onClick: (message: string) => void
}

export default function DemoDiscussions({onClick}: Props) {
  return (
  <>
              <SystemMessageContainer
                hideDecision
                message={{
                  fragments: [
                    {
                      type: "text",
                      text: "What is the expected development of stainless steel market pricing for a specific alloy in the next month?",
                    },
                    {
                      type: "text",
                      text: "What recent news state about possible energy price developments over the next three months?",
                    },
                    {
                      type: "text",
                      text: "What are the most recent patents granted in the area of stainless steel manufacturing?",
                    },
                  ],
                  decision: [],
                  senderRole: "system",
                }}
              />
              <SystemMessageContainer
                hideDecision
                message={{
                  fragments: [
                    {
                      type: "text",
                      text: "Please keep in mind that for this demo I am only capable of answering questions regarding energy prices or steel price predictions.",
                    },
                  ],
                  decision: [],
                  senderRole: "system",
                }}
              />
              {RECOMMENDED_DEMO_MESSAGES.map((demoMsg, idx) => (
                <DemoMessageContainer
                  key={idx}
                  message={demoMsg}
                  onClickCallback={() => onClick(demoMsg)}
                />
              ))}
              </>
  )
}
