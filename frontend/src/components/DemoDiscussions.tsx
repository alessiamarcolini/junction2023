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
                      text: "Hello there!",
                    },
                    {
                      type: "text",
                      text: "Welcome to the EcoGen chatbot service! How can I help you today?",
                    },
                    {
                      type: "text",
                      text: "You might send your own questions or use one of our sample questions below.",
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
