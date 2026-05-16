import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Link from "@tiptap/extension-link"
import Placeholder from "@tiptap/extension-placeholder"
import { useEffect, useRef } from "react"
import {
  Bold,
  Italic,
  List,
  ListOrdered,
  Heading2,
  Link2,
  Undo,
  Redo,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Toggle } from "@/components/ui/toggle"
import { cn } from "@/lib/utils"

interface RichTextEditorProps {
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  className?: string
}

/**
 * Rich text editor component powered by TipTap
 * 
 * Features:
 * - Bold, Italic, Headings (H2)
 * - Bullet and ordered lists
 * - Links (with URL prompt)
 * - Undo/Redo support
 * - Integrates with react-hook-form
 * 
 * @example
 * ```tsx
 * <FormField
 *   control={form.control}
 *   name="description"
 *   render={({ field }) => (
 *     <FormItem>
 *       <FormControl>
 *         <RichTextEditor
 *           value={field.value}
 *           onChange={field.onChange}
 *           placeholder="Enter description..."
 *         />
 *       </FormControl>
 *     </FormItem>
 *   )}
 * />
 * ```
 */

const MenuBar = ({ editor }: { editor: any }) => {
  if (!editor) {
    return null
  }

  const addLink = () => {
    const url = window.prompt("Enter URL:")
    if (url) {
      editor.chain().focus().setLink({ href: url }).run()
    }
  }

  return (
    <div className="border-b border-border p-2 flex flex-wrap gap-1">
      <Toggle
        size="sm"
        pressed={editor.isActive("bold")}
        onPressedChange={() => editor.chain().focus().toggleBold().run()}
      >
        <Bold className="h-4 w-4" />
      </Toggle>
      <Toggle
        size="sm"
        pressed={editor.isActive("italic")}
        onPressedChange={() => editor.chain().focus().toggleItalic().run()}
      >
        <Italic className="h-4 w-4" />
      </Toggle>
      <Toggle
        size="sm"
        pressed={editor.isActive("heading", { level: 2 })}
        onPressedChange={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
      >
        <Heading2 className="h-4 w-4" />
      </Toggle>
      <Toggle
        size="sm"
        pressed={editor.isActive("bulletList")}
        onPressedChange={() => editor.chain().focus().toggleBulletList().run()}
      >
        <List className="h-4 w-4" />
      </Toggle>
      <Toggle
        size="sm"
        pressed={editor.isActive("orderedList")}
        onPressedChange={() => editor.chain().focus().toggleOrderedList().run()}
      >
        <ListOrdered className="h-4 w-4" />
      </Toggle>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={addLink}
        className={cn(
          "h-8 px-2",
          editor.isActive("link") && "bg-accent"
        )}
      >
        <Link2 className="h-4 w-4" />
      </Button>
      <div className="w-px h-6 bg-border mx-1" />
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
      >
        <Undo className="h-4 w-4" />
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
      >
        <Redo className="h-4 w-4" />
      </Button>
    </div>
  )
}

export function RichTextEditor({
  value = "",
  onChange,
  placeholder = "Start typing...",
  className,
}: RichTextEditorProps) {
  // Track if we're updating from external value change (not user input)
  const isUpdatingRef = useRef(false)
  const prevValueRef = useRef(value)
  
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: "text-primary underline",
        },
      }),
      Placeholder.configure({
        placeholder,
      }),
    ],
    content: value,
    onUpdate: ({ editor }) => {
      // Only call onChange if this is a user-initiated update
      if (!isUpdatingRef.current) {
        const html = editor.getHTML()
        onChange?.(html)
      }
    },
    editorProps: {
      attributes: {
        class: cn(
          "focus:outline-none min-h-[150px] px-3 py-2",
          "[&>*]:my-2",
          "[&_h2]:text-xl [&_h2]:font-bold [&_h2]:mt-4 [&_h2]:mb-2",
          "[&_p]:leading-relaxed",
          "[&_ul]:list-disc [&_ul]:ml-6",
          "[&_ol]:list-decimal [&_ol]:ml-6",
          "[&_li]:my-1",
          "[&_a]:text-primary [&_a]:underline",
          "[&_strong]:font-bold",
          "[&_em]:italic",
          className
        ),
      },
    },
  })

  // Update editor content when value changes externally (e.g., form reset, AI assist)
  // Only sync on significant external changes, not on every keystroke
  useEffect(() => {
    if (!editor || editor.isDestroyed) return
    
    // Check if this is an external change (not from user typing)
    const isExternalChange = value !== prevValueRef.current
    
    if (!isExternalChange) return
    
    try {
      const currentContent = editor.getHTML()
      
      // Normalize empty content to avoid unnecessary updates
      const normalizedValue = value || ""
      const normalizedCurrent = currentContent === "<p></p>" ? "" : currentContent
      
      // Only update if the value is actually different
      if (normalizedValue !== normalizedCurrent) {
        isUpdatingRef.current = true
        editor.commands.setContent(normalizedValue)
        // Reset the flag using queueMicrotask for better timing
        queueMicrotask(() => {
          isUpdatingRef.current = false
        })
      }
      
      prevValueRef.current = value
    } catch (error) {
      // Silently handle errors during editor initialization
      console.error("RichTextEditor sync error:", error)
    }
  }, [editor, value])

  return (
    <div className="border border-input rounded-md overflow-hidden bg-background focus-within:ring-1 focus-within:ring-ring">
      {editor && <MenuBar editor={editor} />}
      <EditorContent editor={editor} />
    </div>
  )
}
